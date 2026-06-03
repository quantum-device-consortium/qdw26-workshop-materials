# Workshop Lead Guide

This guide describes how workshop leads add materials to the shared repository
without needing to manage the full deployment stack.

## Contribution Flow

Workshop materials move through this path:

```text
pull request -> CI checks -> merge to main -> published image -> Brev launchable
```

Workshop leads contribute through pull requests. Maintainers review the
materials, update the shared environment when needed, and validate a fresh
workspace from the launchable before participant use.

Planned workshop tracks include:

- Design layout.
- EM simulations.
- Hamiltonian and circuit analysis.
- EM and circuit analysis.

Each track should be represented by a self-contained workshop folder or a
clearly documented section within an existing folder.

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

`workshop.yaml` is the handoff point between workshop content and environment
maintenance. It tells CI what to validate and tells maintainers which
dependencies need to become part of the shared image.

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

Use `entrypoints` for the notebooks participants should open first. Use
`smoke_commands` for fast checks that prove the workshop can start, not for
full simulations.

## Keep Materials Portable

- Use relative paths inside notebooks.
- Keep large generated outputs out of the repo when practical.
- Cite or link reference papers instead of committing PDFs unless redistribution
  rights are explicit.
- Put reusable examples in `shared/` only when more than one workshop needs them.
- Put workshop-only helper files inside the workshop folder.

## Dependency Requests

Add dependency names to `workshop.yaml` first. Maintainers will update the
shared root environment and lock files after checking compatibility with other
workshops.

If a notebook can run in a lighter environment such as Google Colab, note that
in the workshop README. If it requires Palace, GUI forwarding, or another
Brev-specific capability, state that clearly so maintainers can test the right
deployment path.

## Pull Request Checklist

Before requesting review:

- Confirm every notebook and asset referenced by `workshop.yaml` exists.
- Keep notebooks runnable from the repository root or the workshop folder using
  relative paths.
- Add fast `smoke_commands` that prove the workshop can start without running
  long simulations.
- Declare requested Python and system dependencies in `workshop.yaml`.
- Run the local checks listed in `CONTRIBUTING.md` when practical.

Maintainers decide when dependency requests become part of the shared
environment because every added package affects all workshops and the published
image.
