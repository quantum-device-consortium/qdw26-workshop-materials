# Workshop Lead Guide

Workshop leads should be able to add materials without learning the whole environment stack.

## How Changes Reach Attendees

Workshop materials move through this path:

```text
pull request -> CI checks -> merge to main -> published image -> fresh Brev workspace
```

The Brev launchable link is stable, but existing Brev workspaces do not update
automatically. After a pull request is merged, maintainers should test a fresh
workspace created from the launchable before telling attendees that the update
is ready.

Workshop leads should not edit the Brev launchable directly. They should make
repository changes through pull requests.

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

## Pull Request Checklist

Before requesting review:

- Confirm every notebook and asset referenced by `workshop.yaml` exists.
- Keep notebooks runnable from the repository root or the workshop folder using
  relative paths.
- Add fast `smoke_commands` that prove the workshop can start without running
  long simulations.
- Declare requested Python and system dependencies in `workshop.yaml`.
- Run the local checks listed in `CONTRIBUTING.md` when practical.

Maintainers will decide when dependency requests become part of the shared
environment, because every added package affects all workshops and the attendee
image.
