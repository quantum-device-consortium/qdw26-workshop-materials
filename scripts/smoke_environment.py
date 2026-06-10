#!/usr/bin/env python3
"""Run quick checks for the shared workshop environment."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from validate_workshops import discover_workshop_dirs, parse_manifest

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: Path = ROOT) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def run_shell(command: str, cwd: Path) -> None:
    print("+", command)
    subprocess.run(command, cwd=cwd, shell=True, check=True, executable="/bin/bash")


def require_command(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"Required command not found: {name}")


def require_module(*names: str) -> None:
    if not any(importlib.util.find_spec(name) is not None for name in names):
        raise RuntimeError(f"Required Python module not found: {' or '.join(names)}")


def check_palace_runtime() -> None:
    print("+ Palace runtime")
    palace_bin = os.environ["PALACE_BIN"]
    if not Path(palace_bin).is_file():
        raise RuntimeError(f"PALACE_BIN does not point to a file: {palace_bin}")
    run([palace_bin, "--version"])
    from qdw_workshop.palace import install_sqdmetal_palace_runner

    install_sqdmetal_palace_runner()


def check_sqdmetal_imports() -> None:
    print("+ SQDMetal workshop component imports")
    import pyvista as pv
    from vtkmodules.vtkCommonCore import vtkVersion
    from SQDMetal.Comps.Capacitors import CapacitorProngPin
    from SQDMetal.Comps.Junctions import JunctionDolanPinStretch
    from SQDMetal.Comps.Xmon import Xmon

    print(f"vtkmodules {vtkVersion.GetVTKVersion()}")
    print(f"pyvista {pv.__version__}")
    assert Xmon is not None
    assert JunctionDolanPinStretch is not None
    assert CapacitorProngPin is not None


def check_jupyter_kernel() -> None:
    print("+ jupyter kernel readiness")
    from jupyter_client.manager import KernelManager

    kernel_manager = KernelManager(kernel_name="python3")
    kernel_manager.start_kernel()
    kernel_client = kernel_manager.client()
    kernel_client.start_channels()
    try:
        kernel_client.wait_for_ready(timeout=30)
        kernel_client.execute("import qiskit_metal as qm; print(qm.__version__)")
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            try:
                message = kernel_client.get_iopub_msg(timeout=5)
            except Exception:
                continue
            if (
                message["header"]["msg_type"] == "status"
                and message["content"].get("execution_state") == "idle"
            ):
                break
        else:
            raise RuntimeError("Jupyter kernel did not finish importing qiskit_metal")
    finally:
        kernel_client.stop_channels()
        kernel_manager.shutdown_kernel(now=True)


def main() -> int:
    run([sys.executable, "--version"])
    run([sys.executable, "-m", "jupyter", "--version"])
    check_jupyter_kernel()
    require_command("palace")
    run(["palace", "--version"])
    check_palace_runtime()
    require_command("gmsh")
    run(["gmsh", "--version"])
    require_command("paraview")
    require_command("pvpython")
    run(["pvpython", "--version"])
    require_command("pvbatch")
    run(["pvbatch", "--version"])
    require_command("klayout")
    run(["klayout", "-v"])
    require_module("qiskit_metal")
    require_module("SQDMetal", "sqdmetal")
    require_module("klayout")
    require_module("meshwell")
    require_module("pypalace")
    require_module("skrf")
    require_module("scqubits")
    require_module("squadds")
    check_sqdmetal_imports()

    for workshop_dir in discover_workshop_dirs():
        manifest = parse_manifest(workshop_dir / "workshop.yaml")
        commands = manifest.get("smoke_commands", [])
        if not isinstance(commands, list):
            raise RuntimeError(f"{workshop_dir}/workshop.yaml: smoke_commands must be a list")
        for command in commands:
            if not isinstance(command, str):
                raise RuntimeError(f"{workshop_dir}/workshop.yaml: smoke command must be a string")
            run_shell(command, workshop_dir)

    print("Environment smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
