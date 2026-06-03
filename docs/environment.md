# Shared Environment

The repository root defines the environment used by all workshops.

## Files

- `Dockerfile`: system packages, Palace base image, Python runtime, and `uv`.
- `pyproject.toml`: Python dependency requests that are installed into the shared environment.
- `uv.lock`: locked Python resolution.
- `compose.yaml`: local development runtime that can build from source.
- `compose.deploy.yaml`: hosted runtime that pulls the published GHCR image.

Core system tools include Palace, Gmsh, and ParaView. Headless checks use
ParaView's `pvpython` and `pvbatch` commands. The `paraview` GUI executable is
available when users connect with a compatible display environment. See
[GUI forwarding](gui-forwarding.md) for optional desktop-window setup.

## Dependency Policy

Workshop leads declare requested dependencies in their `workshop.yaml`.
Maintainers update the shared root environment so all sessions use one
consistent setup.

## Image

The canonical image target is:

```text
ghcr.io/quantum-device-consortium/qdw-workshop-materials
```

CI publishes `main` and `sha-<shortsha>` tags after successful builds on `main`.
The image contains the shared environment and the repository materials at `/home/ubuntu/qdw-workshop-materials`.

Use `compose.deploy.yaml` when the goal is to run the same image that CI published. Use `compose.yaml` when actively developing or testing Dockerfile changes.

Deployment security notes live in `docs/deployment-security.md`.

## Lifecycle

Environment changes should follow this path:

1. Workshop leads declare dependency needs in `workshop.yaml`.
2. Maintainers update `Dockerfile`, `pyproject.toml`, and `uv.lock`.
3. Pull request checks validate manifests, notebooks, Compose config, and smoke
   tests.
4. Merges to `main` publish the GHCR image.
5. Maintainers create a fresh hosted workspace and run the Brev smoke checks
   before participant use.

The Brev launchable should usually remain stable. Update the launchable only
when the repository URL, Compose file path, hardware profile, storage size, or
intended access model changes.

## Smoke Checks

Smoke checks should confirm the environment can start and workshops can be opened. They should not run long simulations in pull requests.
