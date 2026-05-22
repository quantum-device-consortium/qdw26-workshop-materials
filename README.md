# QDW Workshop Materials

Joint workspace for Quantum Device Workshop materials and the shared environment used by workshop attendees.

## What Lives Here

- `Dockerfile`, `compose.yaml`, `compose.deploy.yaml`, `pyproject.toml`, `uv.lock`: shared runtime environment.
- `workshops/`: self-contained workshop folders, each with a `workshop.yaml` manifest.
- `shared/`: examples and files intended for more than one workshop.
- `docs/`: attendee, workshop lead, Brev, environment, and deployment security notes.
- `scripts/`: validation, smoke-test, and Brev setup helpers.

## Quick Start

Use whichever access path fits your workflow. All paths should point at the same checked-out materials and shared environment.

```bash
docker compose up --build
```

Then choose an interface:

- JupyterLab: `docker compose exec dev uv run jupyter lab --ip 0.0.0.0 --port 8888 --no-browser`
- Shell: `docker compose exec dev bash`
- VS Code or Cursor: attach to the running `dev` container.
- SSH on Brev: connect to the instance, then use Docker Compose from the repo checkout.

Brev/attendee deployments should use the published image:

```bash
docker compose -f compose.deploy.yaml up -d
```

## Current Workshops

- `workshops/quantum-device-design/`: Qiskit Metal, Palace, and SQDMetal tutorial materials.

## Contributor Checks

Before opening a pull request:

```bash
python scripts/validate_workshops.py
python scripts/check_notebooks.py
bash -n scripts/*.sh
docker compose config
docker compose -f compose.deploy.yaml config
```

If Docker is running locally, also build and smoke-test the image:

```bash
docker build -t qdw-workshop-materials:local .
docker run --rm qdw-workshop-materials:local python scripts/smoke_environment.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/workshop-lead-guide.md](docs/workshop-lead-guide.md) for the workflow for adding or updating workshop materials.
See [docs/deployment-security.md](docs/deployment-security.md) for deployment security expectations.
