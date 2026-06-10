from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from scripts.validate_workshops import validate_manifest
from scripts.run_workshop_execution import discover_execution_targets


class WorkshopExecutionTargetTests(unittest.TestCase):
    def write_workshop(self, manifest: str) -> Path:
        root = Path(tempfile.mkdtemp())
        workshop_dir = root / "example-workshop"
        (workshop_dir / "notebooks").mkdir(parents=True)
        (workshop_dir / "scripts").mkdir()
        (workshop_dir / "assets").mkdir()
        (workshop_dir / "README.md").write_text("# Example\n", encoding="utf-8")
        (workshop_dir / "assets" / "image.png").write_text("placeholder", encoding="utf-8")
        (workshop_dir / "notebooks" / "lesson.ipynb").write_text(
            '{"cells":[],"metadata":{},"nbformat":4,"nbformat_minor":5}',
            encoding="utf-8",
        )
        (workshop_dir / "scripts" / "demo.py").write_text("print('ok')\n", encoding="utf-8")
        (workshop_dir / "workshop.yaml").write_text(manifest, encoding="utf-8")
        return workshop_dir

    def base_manifest(self, execution_targets: str = "") -> str:
        return f"""slug: example-workshop
title: Example Workshop
leads:
  - maintainer
summary: Example materials.
entrypoints:
  - path: notebooks/lesson.ipynb
    kind: notebook
    description: Lesson notebook.
notebooks:
  - notebooks/lesson.ipynb
assets:
  - assets/image.png
python_dependencies:
  - jupyter
system_dependencies:
  - palace
smoke_commands:
  - test -f notebooks/lesson.ipynb
{execution_targets}"""

    def test_manifest_requires_execution_targets(self) -> None:
        workshop_dir = self.write_workshop(self.base_manifest())

        errors = validate_manifest(workshop_dir)

        self.assertIn("missing required fields: execution_targets", "\n".join(errors))

    def test_manifest_validates_execution_target_files_and_kinds(self) -> None:
        workshop_dir = self.write_workshop(
            self.base_manifest(
                """execution_targets:
  - path: notebooks/missing.ipynb
    kind: notebook
  - path: scripts/demo.py
    kind: shell
"""
            )
        )

        errors = "\n".join(validate_manifest(workshop_dir))

        self.assertIn("missing execution target 'notebooks/missing.ipynb'", errors)
        self.assertIn("execution target kind must be one of notebook, python", errors)

    def test_manifest_accepts_notebook_and_python_execution_targets(self) -> None:
        workshop_dir = self.write_workshop(
            self.base_manifest(
                """execution_targets:
  - path: notebooks/lesson.ipynb
    kind: notebook
    timeout_seconds: 120
  - path: scripts/demo.py
    kind: python
    timeout_seconds: 30
"""
            )
        )

        self.assertEqual(validate_manifest(workshop_dir), [])

    def test_execution_runner_discovers_manifest_targets(self) -> None:
        workshop_dir = self.write_workshop(
            self.base_manifest(
                """execution_targets:
  - path: notebooks/lesson.ipynb
    kind: notebook
    timeout_seconds: 120
  - path: scripts/demo.py
    kind: python
    timeout_seconds: 30
"""
            )
        )

        import scripts.run_workshop_execution as runner

        original_discover = runner.discover_workshop_dirs
        try:
            runner.discover_workshop_dirs = lambda: [workshop_dir]
            targets = discover_execution_targets(default_timeout=900)
        finally:
            runner.discover_workshop_dirs = original_discover

        self.assertEqual([target.kind for target in targets], ["notebook", "python"])
        self.assertEqual([target.timeout_seconds for target in targets], [120, 30])
        self.assertEqual([target.path.name for target in targets], ["lesson.ipynb", "demo.py"])


if __name__ == "__main__":
    unittest.main()
