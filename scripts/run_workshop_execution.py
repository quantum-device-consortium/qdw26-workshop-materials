#!/usr/bin/env python3
"""Run declared workshop execution targets and record benchmark data."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from typing import Callable

try:
    from validate_workshops import ROOT, discover_workshop_dirs, parse_manifest
except ModuleNotFoundError:
    from scripts.validate_workshops import ROOT, discover_workshop_dirs, parse_manifest


@dataclass(frozen=True)
class ExecutionTarget:
    workshop: str
    path: Path
    kind: str
    timeout_seconds: int


@dataclass
class ExecutionResult:
    workshop: str
    path: str
    kind: str
    status: str
    duration_seconds: float
    peak_rss_mb: float
    disk_delta_mb: float
    message: str = ""


class ResourceSampler:
    def __init__(self, root: Path) -> None:
        self.root = root
        import psutil

        self.process = psutil.Process(os.getpid())
        self.start_disk_bytes = directory_size(root)
        self.peak_rss_bytes = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._sample, daemon=True)

    def __enter__(self) -> "ResourceSampler":
        self._thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self._stop.set()
        self._thread.join(timeout=5)

    def _sample(self) -> None:
        while not self._stop.is_set():
            self.peak_rss_bytes = max(self.peak_rss_bytes, process_tree_rss(self.process))
            self._stop.wait(1)

    @property
    def peak_rss_mb(self) -> float:
        return self.peak_rss_bytes / (1024 * 1024)

    @property
    def disk_delta_mb(self) -> float:
        return (directory_size(self.root) - self.start_disk_bytes) / (1024 * 1024)


def directory_size(root: Path) -> int:
    total = 0
    for path in root.rglob("*"):
        try:
            if path.is_file():
                total += path.stat().st_size
        except OSError:
            continue
    return total


def process_tree_rss(process: psutil.Process) -> int:
    import psutil

    processes = [process]
    try:
        processes.extend(process.children(recursive=True))
    except psutil.Error:
        pass

    total = 0
    for item in processes:
        try:
            total += item.memory_info().rss
        except psutil.Error:
            continue
    return total


def parse_timeout(raw_timeout: object | None, default_timeout: int) -> int:
    if raw_timeout is None:
        return default_timeout
    return int(str(raw_timeout))


def discover_execution_targets(default_timeout: int) -> list[ExecutionTarget]:
    targets: list[ExecutionTarget] = []
    for workshop_dir in discover_workshop_dirs():
        manifest = parse_manifest(workshop_dir / "workshop.yaml")
        raw_targets = manifest.get("execution_targets", [])
        if not isinstance(raw_targets, list):
            raise ValueError(f"{workshop_dir / 'workshop.yaml'}: execution_targets must be a list")
        for raw_target in raw_targets:
            if not isinstance(raw_target, dict):
                raise ValueError(f"{workshop_dir / 'workshop.yaml'}: execution target must be a mapping")
            target_path = raw_target.get("path")
            target_kind = raw_target.get("kind")
            if not isinstance(target_path, str) or not isinstance(target_kind, str):
                raise ValueError(f"{workshop_dir / 'workshop.yaml'}: execution target requires path and kind")
            targets.append(
                ExecutionTarget(
                    workshop=workshop_dir.name,
                    path=workshop_dir / target_path,
                    kind=target_kind,
                    timeout_seconds=parse_timeout(raw_target.get("timeout_seconds"), default_timeout),
                )
            )
    return targets


def run_notebook(path: Path, timeout_seconds: int) -> None:
    import nbformat
    from nbclient import NotebookClient

    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=timeout_seconds,
        kernel_name="python3",
        resources={"metadata": {"path": str(path.parent)}},
        allow_errors=False,
    )
    client.execute()


def run_python(path: Path, timeout_seconds: int) -> None:
    subprocess.run(
        [sys.executable, str(path)],
        cwd=path.parent,
        timeout=timeout_seconds,
        check=True,
    )


def run_target(target: ExecutionTarget) -> ExecutionResult:
    start = time.monotonic()
    runner: Callable[[Path, int], None]
    if target.kind == "notebook":
        runner = run_notebook
    elif target.kind == "python":
        runner = run_python
    else:
        raise ValueError(f"Unsupported execution target kind: {target.kind}")

    with ResourceSampler(ROOT) as sampler:
        try:
            runner(target.path, target.timeout_seconds)
        except Exception as exc:
            return ExecutionResult(
                workshop=target.workshop,
                path=str(target.path.relative_to(ROOT)),
                kind=target.kind,
                status="failed",
                duration_seconds=time.monotonic() - start,
                peak_rss_mb=sampler.peak_rss_mb,
                disk_delta_mb=sampler.disk_delta_mb,
                message=f"{type(exc).__name__}: {exc}",
            )

    return ExecutionResult(
        workshop=target.workshop,
        path=str(target.path.relative_to(ROOT)),
        kind=target.kind,
        status="passed",
        duration_seconds=time.monotonic() - start,
        peak_rss_mb=sampler.peak_rss_mb,
        disk_delta_mb=sampler.disk_delta_mb,
    )


def write_results(results: list[ExecutionResult], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [asdict(result) for result in results]
    (output_dir / "workshop-execution-results.json").write_text(
        json.dumps(rows, indent=2) + "\n",
        encoding="utf-8",
    )
    with open(output_dir / "workshop-execution-results.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "benchmark-results")
    parser.add_argument("--default-timeout", type=int, default=900)
    args = parser.parse_args()

    targets = discover_execution_targets(args.default_timeout)
    if not targets:
        print("No workshop execution targets declared.", file=sys.stderr)
        return 1

    results: list[ExecutionResult] = []
    for target in targets:
        print(f"+ executing {target.kind}: {target.path.relative_to(ROOT)}", flush=True)
        result = run_target(target)
        results.append(result)
        print(
            f"  {result.status} in {result.duration_seconds:.1f}s, "
            f"peak RSS {result.peak_rss_mb:.1f} MiB, "
            f"disk delta {result.disk_delta_mb:.1f} MiB",
            flush=True,
        )
        if result.message:
            print(f"  {result.message}", flush=True)

    write_results(results, args.output_dir)
    failures = [result for result in results if result.status != "passed"]
    if failures:
        print(f"{len(failures)} execution target(s) failed.", file=sys.stderr)
        return 1

    print(f"Executed {len(results)} workshop target(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
