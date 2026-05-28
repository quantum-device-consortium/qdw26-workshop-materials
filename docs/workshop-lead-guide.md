# Workshop Lead Guide

Workshop leads should be able to add materials without learning the whole environment stack.

## Add A Workshop

Create a folder under `workshops/`:

```text
workshops/<slug>/
  README.md
  workshop.yaml
  notebooks/
  assets/
  references/
```

Use a short lowercase slug, for example `quantum-device-design`.

## Fill Out The Manifest

`workshop.yaml` is the handoff point between workshop leads and environment maintainers. It tells CI what to validate and tells maintainers which dependencies need to become part of the shared image.

Required fields:

- `slug`
- `title`
- `leads`
- `summary`
- `entrypoints`
- `notebooks`
- `assets`
- `python_dependencies`
- `system_dependencies`
- `smoke_commands`

Use `entrypoints` for the notebooks attendees should open first. Use `smoke_commands` for fast checks that prove the workshop can start, not for full simulations.

## Keep Materials Portable

- Use relative paths inside notebooks.
- Keep large generated outputs out of the repo when practical.
- Cite or link reference papers instead of committing PDFs unless redistribution
  rights are explicit.
- Put reusable examples in `shared/` only when more than one workshop needs them.
- Put workshop-only helper files inside the workshop folder.

## Dependency Requests

Add dependency names to `workshop.yaml` first. Maintainers will update the shared root environment and lock files after checking compatibility with other workshops.
