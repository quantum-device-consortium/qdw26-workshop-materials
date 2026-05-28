# Deployment Security

This repository is intended for a workshop environment where attendees use a shared, prebuilt runtime without handling maintainer credentials.

## Trust Boundaries

- GitHub stores source materials, CI configuration, and the Docker build definition.
- GitHub Actions builds and publishes the canonical image to GHCR.
- Brev runs the published image and exposes approved access paths to attendees.
- Attendees should never receive repository deploy keys, package tokens, maintainer credentials, or cloud-provider credentials.

## Repository Access

The current deployment mode uses a public GitHub repository so Brev can clone
the materials without repository credentials. This is the simplest attendee
path and keeps Brev setup reproducible.

If the repository is made private again, use a read-only deploy key for Brev
to clone it. Scope the deploy key only to this repository and do not reuse it
elsewhere.

A fine-grained GitHub token can be used for repository-clone testing, but it should be time-limited and restricted to the minimum required permissions:

- Repository contents: read-only for this repository.

Do not commit tokens, private SSH keys, `.env` files, license files, or generated Docker auth files.

Local-only planning notes and local credential files are ignored by both Git and Docker build context rules so they do not enter published images.

## GHCR Access

The intended attendee deployment uses a public GHCR image so Brev and attendee
machines can pull it without package credentials.

Public image visibility means the image layers are public. Do not bake private
workshop materials, secrets, license files, proprietary installers, or private
datasets into the image.

If the workshop image is private, Brev needs package read access to pull it. GitHub currently documents GHCR Docker authentication outside GitHub Actions with a personal access token classic that has `read:packages`. Prefer a short-lived token and a Brev secret mechanism if available.

`scripts/brev-setup.sh` accepts `GHCR_USERNAME` and `GHCR_TOKEN` for image pulls. When those variables are used, the script writes Docker auth to a temporary Docker config directory and removes it before exiting. This avoids leaving package credentials in the Brev user's normal Docker configuration.

Keep the image private if it contains private workshop materials or licensing constraints.

## Brev Runtime

Use `compose.deploy.yaml` for Brev deployments. It pulls the already-published image instead of rebuilding on the instance.

The deployment compose file defaults to binding Jupyter on `127.0.0.1:8888`. Override `QDW_JUPYTER_BIND=0.0.0.0` only when the Brev access layer requires it and the instance is protected by Brev authentication or another access control layer.

The container drops Linux capabilities and uses `no-new-privileges` by default. Do not add privileged mode, Docker socket mounts, host filesystem mounts, or broad network exposure for attendee-facing deployments unless there is a documented reason and review.

## Attendee Isolation

A single shared container is not a strong multi-user security boundary. Attendees using the same Unix account, container, or writable workspace may be able to see or modify each other's files.

For attendee-facing use, prefer one of these patterns:

- One Brev instance per attendee or small trusted group.
- A managed multi-user JupyterHub-style deployment with per-user accounts and isolated storage.
- Read-only shared materials plus separate per-user working directories.

Do not treat one shared Docker container as suitable isolation for untrusted arbitrary code from many attendees.

## CI Permissions

GitHub Actions workflows should use least privilege:

- Validation and Docker smoke jobs should only need repository read access.
- Image publishing needs package write access.
- Nightly smoke needs package read access.

Avoid adding broad `contents: write`, repository administration, secrets write, or cloud credential permissions unless a workflow explicitly requires them.

## Dependency Security

Dependency changes should update `pyproject.toml` and `uv.lock` together. Before merging dependency changes, run:

```bash
python scripts/validate_workshops.py
python scripts/check_notebooks.py
bash -n scripts/*.sh
docker compose config
docker compose -f compose.deploy.yaml config
uv run --with pip-audit pip-audit --progress-spinner off
```

Keep Dependabot alerts at zero before attendee deployment. Treat stale alerts as unresolved until local audit, GitHub SBOM, and Dependabot alert state agree.

## Incident Response

If a token, deploy key, license file, or other secret is exposed:

1. Revoke the credential immediately.
2. Remove the secret from the repository and any images that included it.
3. Rotate any dependent credentials.
4. Audit GitHub Actions logs, GHCR image history, and Brev shell history for exposure.
5. Rebuild and republish a clean image.
