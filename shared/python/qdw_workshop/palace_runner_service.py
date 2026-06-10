"""Helper process for launching Palace commands from notebook kernels."""

from __future__ import annotations

import json
from pathlib import Path
import socket
import subprocess
import sys


def handle_request(raw_line: str) -> dict[str, str]:
    request = json.loads(raw_line)
    command = request["command"]
    cwd = Path(request["cwd"])
    log_path = Path(request["log_path"])
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "w", encoding="utf-8") as log_file:
        result = subprocess.run(
            command,
            cwd=cwd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

    if result.returncode == 0:
        return {"status": "ok"}

    log_tail = log_path.read_text(errors="replace")[-4000:]
    return {
        "status": "error",
        "message": (
            f"Palace exited with status {result.returncode}. "
            f"See {log_path}.\n{log_tail}"
        ),
    }


def serve_stdio() -> int:
    for raw_line in sys.stdin:
        try:
            response = handle_request(raw_line)
        except Exception as exc:
            response = {"status": "error", "message": f"{type(exc).__name__}: {exc}"}
        print(json.dumps(response), flush=True)
    return 0


def serve_socket(socket_path: Path) -> int:
    socket_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        socket_path.unlink()
    except FileNotFoundError:
        pass

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
        server.bind(str(socket_path))
        socket_path.chmod(0o600)
        server.listen()
        while True:
            connection, _ = server.accept()
            with connection:
                raw_line = connection.makefile("r", encoding="utf-8").readline()
                try:
                    response = handle_request(raw_line)
                except Exception as exc:
                    response = {"status": "error", "message": f"{type(exc).__name__}: {exc}"}
                connection.sendall((json.dumps(response) + "\n").encode("utf-8"))


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--socket":
        return serve_socket(Path(sys.argv[2]))
    return serve_stdio()


if __name__ == "__main__":
    raise SystemExit(main())
