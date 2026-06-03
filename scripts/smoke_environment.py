#!/usr/bin/env python3
"""Run quick checks for the shared workshop environment."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys

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


def main() -> int:
    run([sys.executable, "--version"])
    run([sys.executable, "-m", "jupyter", "--version"])
    require_command("palace")
    run(["palace", "--version"])
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
