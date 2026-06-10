"""Palace execution helpers for workshop notebooks."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import threading
import json
import socket


def palace_cpu_count(default: int) -> int:
    """Return a portable Palace CPU count for local, CI, and hosted runs."""

    requested = int(os.environ.get("QDW_PALACE_CPUS", str(default)))
    available = os.cpu_count() or 1
    return max(1, min(requested, available))


def capacitance_dataframe(cap_matrix, labels: list[str], order: list[str] | None = None):
    """Return a labeled capacitance matrix in fF from SQDMetal Palace output."""

    import pandas as pd

    cdf = pd.DataFrame(cap_matrix * 1e15)
    if cdf.shape[1] == len(labels) + 1:
        cdf = cdf.iloc[:, 1:]

    expected_shape = (len(labels), len(labels))
    if cdf.shape != expected_shape:
        raise ValueError(
            f"Expected capacitance matrix shape {expected_shape} or "
            f"({len(labels)}, {len(labels) + 1}), got {cdf.shape}"
        )

    cdf.columns = labels
    cdf.index = labels
    if order is not None:
        cdf = cdf.reindex(index=order, columns=order)
    return cdf


def display_eigenmode_image(output_dir: str | Path, mode_num: int):
    """Display a Palace eigenmode image when the requested mode image exists."""

    from IPython.display import Image, display

    output_path = Path(output_dir)
    image_path = output_path / f"eig{mode_num}_ErealMag.png"
    if not image_path.exists():
        candidates = sorted(output_path.glob("eig*_ErealMag.png"))
        if not candidates:
            print(f"No eigenmode field images found in {output_path}")
            return None
        image_path = candidates[min(mode_num, len(candidates) - 1)]
        print(f"Requested eig{mode_num}_ErealMag.png was not found; displaying {image_path.name}.")

    return display(Image(filename=str(image_path)))


class PalaceRunnerService:
    """Small helper process used to launch Palace from a clean process state."""

    def __init__(self) -> None:
        self.process = subprocess.Popen(
            [sys.executable, "-m", "qdw_workshop.palace_runner_service"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._lock = threading.Lock()

    def run(self, command: list[str], cwd: Path, log_path: Path) -> None:
        if self.process.poll() is not None:
            raise RuntimeError("Palace runner service exited before the command was submitted")
        if self.process.stdin is None or self.process.stdout is None:
            raise RuntimeError("Palace runner service pipes are unavailable")

        request = {
            "command": command,
            "cwd": str(cwd),
            "log_path": str(log_path),
        }
        with self._lock:
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            response_line = self.process.stdout.readline()

        if not response_line:
            stderr = ""
            if self.process.stderr is not None:
                stderr = self.process.stderr.read()
            raise RuntimeError(f"Palace runner service stopped without a response. {stderr}")

        response = json.loads(response_line)
        if response.get("status") != "ok":
            message = response.get("message", "Palace command failed")
            raise RuntimeError(str(message))


_PALACE_RUNNER_SERVICE: PalaceRunnerService | None = None


def palace_runner_socket() -> Path:
    return Path(os.environ.get("QDW_PALACE_RUNNER_SOCKET", "/tmp/qdw-palace-runner.sock"))


def run_with_socket(command: list[str], cwd: Path, log_path: Path) -> bool:
    socket_path = palace_runner_socket()
    if not socket_path.exists():
        return False

    request = {
        "command": command,
        "cwd": str(cwd),
        "log_path": str(log_path),
    }
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(str(socket_path))
        client.sendall((json.dumps(request) + "\n").encode("utf-8"))
        response_line = client.makefile("r", encoding="utf-8").readline()

    response = json.loads(response_line)
    if response.get("status") != "ok":
        message = response.get("message", "Palace command failed")
        raise RuntimeError(str(message))
    return True


def ensure_palace_runner_service() -> None:
    """Start the Palace helper process before notebooks import heavy GUI stacks."""

    if palace_runner_socket().exists():
        return

    global _PALACE_RUNNER_SERVICE
    if _PALACE_RUNNER_SERVICE is not None and _PALACE_RUNNER_SERVICE.process.poll() is None:
        return
    _PALACE_RUNNER_SERVICE = PalaceRunnerService()


def run_palace(command: list[str], cwd: Path, log_path: Path) -> None:
    if run_with_socket(command, cwd, log_path):
        return

    if _PALACE_RUNNER_SERVICE is not None and _PALACE_RUNNER_SERVICE.process.poll() is None:
        _PALACE_RUNNER_SERVICE.run(command, cwd, log_path)
        return

    with open(log_path, "w", encoding="utf-8") as log_file:
        result = subprocess.run(
            command,
            cwd=cwd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

    if result.returncode != 0:
        log_tail = log_path.read_text(errors="replace")[-4000:]
        raise RuntimeError(
            f"Palace exited with status {result.returncode}. "
            f"See {log_path}.\n{log_tail}"
        )


def install_sqdmetal_renderer_compat() -> None:
    """Keep SQDMetal's geometry processor compatible with current Quantum Metal."""

    from SQDMetal.Utilities import QUtilities
    from SQDMetal.Utilities.GeometryProcessors import GeomQiskitMetal

    current_renderer = GeomQiskitMetal.QiskitShapelyRenderer
    if getattr(current_renderer, "_qdw_compat_renderer", False):
        return

    class QDWQiskitShapelyRenderer(current_renderer):
        def __init__(self, *args, **kwargs):
            if len(args) == 3 and args[1] is not None:
                super().__init__(args[1], **kwargs)
            else:
                super().__init__(*args, **kwargs)

    QDWQiskitShapelyRenderer._qdw_compat_renderer = True
    GeomQiskitMetal.QiskitShapelyRenderer = QDWQiskitShapelyRenderer
    QUtilities.QiskitShapelyRenderer = QDWQiskitShapelyRenderer


def install_sqdmetal_palace_runner() -> None:
    """Use a deterministic Palace launcher for SQDMetal notebook runs.

    SQDMetal's default local runner writes a temporary shell script and launches it
    through ``shell=True``. That path can block inside notebook kernels on the
    Linux container used for the workshop. This compatibility hook keeps
    SQDMetal's simulation preparation and result parsing intact, but replaces the
    process launch with a direct subprocess call to ``PALACE_BIN``.
    """

    install_sqdmetal_renderer_compat()

    from SQDMetal.PALACE.Model import PALACE_Model_Base

    current_runner = PALACE_Model_Base._run_local
    if getattr(current_runner, "_qdw_safe_runner", False):
        return

    def _run_local(self) -> None:
        config_file = Path(self._sim_config).resolve()
        config_dir = config_file.parent
        output_dir = Path(self._output_data_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        palace_bin = Path(getattr(self, "palace_dir", "") or os.environ["PALACE_BIN"]).expanduser()
        if not palace_bin.is_file() or not os.access(palace_bin, os.X_OK):
            raise FileNotFoundError(f"Palace executable is not available: {palace_bin}")

        self.log_location = str(output_dir / "out.log")
        command = [
            str(palace_bin),
            "-np",
            str(self._num_cpus),
            "-nt",
            str(self._num_threads),
            config_file.name,
        ]

        run_palace(command, config_dir, Path(self.log_location))
        self.cur_process = None

    _run_local._qdw_safe_runner = True
    PALACE_Model_Base._run_local = _run_local


def install_pypalace_runner() -> None:
    """Use the workshop Palace launcher for pyPalace simulations.

    pyPalace normally starts Palace directly from the notebook kernel with
    ``subprocess.Popen``. In the workshop container, launching MPI-heavy jobs
    from a long-running notebook kernel can stall before the Palace process is
    created. This hook keeps pyPalace's configuration and result parsing intact
    while delegating the actual Palace process launch to the same isolated
    helper used by the SQDMetal notebooks.
    """

    from pypalace import Simulation

    current_runner = Simulation.run
    if getattr(current_runner, "_qdw_safe_runner", False):
        return

    def _run(self, n, HPC_options=None, custom_script_name=None) -> None:
        if HPC_options is not None:
            return current_runner(self, n, HPC_options=HPC_options, custom_script_name=custom_script_name)

        if self.config.saved is False:
            self.config.save_config()

        cwd = Path.cwd()
        output_dir = Path(self.config.config["Problem"]["Output"])
        output_dir.mkdir(parents=True, exist_ok=True)
        log_path = output_dir / "out.log"
        command = ["mpirun", "-n", str(n), self.path_to_palace, self.path_to_json]

        run_palace(command, cwd, log_path)
        print(f"Palace completed successfully. Log written to {log_path}.")

    _run._qdw_safe_runner = True
    Simulation.run = _run
