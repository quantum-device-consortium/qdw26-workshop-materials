# Contributing

This repository contains shared workshop materials and the common runtime
environment.

## Workflow

1. Create a branch for your workshop or update.
2. Keep workshop files inside `workshops/<slug>/`.
3. Update that workshop's `workshop.yaml` whenever you add notebooks, assets, dependency needs, or smoke checks.
4. Run the local checks before opening a pull request.
5. Open a pull request against `main`.

## Local Checks

```bash
python scripts/validate_workshops.py
python scripts/check_notebooks.py
bash -n scripts/*.sh
docker compose config
docker compose -f compose.deploy.yaml config
```

If Docker is running:

```bash
docker build -t qdw-workshop-materials:local .
docker run --rm qdw-workshop-materials:local python scripts/smoke_environment.py
```

## Workshop Folder Contract

Every workshop folder must include:

- `README.md`: what the workshop covers and where to start.
- `workshop.yaml`: manifest used by CI and the shared environment.
- `notebooks/`: notebooks used by participants.
- `assets/`: images or small files used by the notebooks.
- `references/`: papers, background material, and reading.

Workshop-specific legacy setup files can stay in the workshop folder. Shared tools and environment dependencies belong at the repository root.

## Dependencies

Workshop leads should declare requested dependencies in `workshop.yaml`.
Maintainers consolidate those requests into the shared `Dockerfile`,
`pyproject.toml`, and `uv.lock` so all workshops use one environment.

## Access Paths

The shared environment should support multiple access styles:

- JupyterLab for notebook-first work.
- VS Code or Cursor for editor-first work.
- SSH for terminal-first work.
- Docker Compose for local development.

Avoid changes that make one access path work by breaking another.
