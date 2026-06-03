# Upstream QDW Playground Notes

The original QDW playground environment was imported from
`abhishekchak52/qdw26-playground`. The current repository supersedes that
standalone setup by combining the shared environment with workshop materials.

## Local Docker Pattern

The upstream pattern used Docker Compose to build a development container,
mount the repository, synchronize Python dependencies with `uv`, and keep the
container running for interactive work.

```bash
docker compose up --build
docker compose exec dev bash
docker compose exec dev palace --version
```

This repository keeps the same basic pattern while adding workshop manifests,
validation scripts, CI, GHCR publishing, and hosted deployment documentation.

## Brev Pattern

The upstream Brev workflow used a Docker Compose launchable. The current
workshop deployment should also use Docker Compose mode, with this repository
as the source and the current GHCR image as the runtime image.

See [brev.md](brev.md) for the active release process.
