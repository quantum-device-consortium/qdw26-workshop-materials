# Brev Deployment

Brev is the hosted compute option for workshop sessions that need the full
preinstalled environment.

## How It Works

```text
GitHub repository -> GitHub Actions -> GHCR image -> Brev launchable -> participant workspace
```

- The repository stores workshop materials, environment files, and validation scripts.
- GitHub Actions validates changes and publishes the workshop image.
- The Brev launchable uses the current repository and Docker Compose setup.
- Participants receive a credit code and launchable access instructions through workshop channels.
- Participants use the launchable to create their own workspace.

Workspace sizing, credit-code distribution, and participant access details will
be finalized separately before the workshop.

## Launchable Requirements

The workshop launchable should use:

- Repository: `https://github.com/quantum-device-consortium/qdw26-workshop-materials`
- Mode: Docker Compose
- Compose file: `compose.yaml`
- Image: `ghcr.io/quantum-device-consortium/qdw-workshop-materials:main`

Keep the launchable aligned with `main`. Existing workspaces do not update
automatically after repository changes, so final workshop testing should use a
fresh workspace created from the launchable.

## Release Checklist

Before distributing participant instructions:

1. Merge workshop updates through pull requests.
2. Confirm GitHub Actions passes on `main`.
3. Confirm the GHCR image publish workflow succeeds.
4. Create a fresh Brev test workspace from the launchable.
5. Run the smoke checks below.
6. Verify the required access paths for the workshop.
7. Confirm workspace configuration, credit-code distribution, and support plan.

## Smoke Checks

Run these inside a fresh Brev workspace:

```bash
cd qdw-workshop-materials
docker compose ps
docker compose exec dev python scripts/smoke_environment.py
docker compose exec dev python scripts/validate_workshops.py
docker compose exec dev python scripts/check_notebooks.py
```

Run the checks again whenever workshop notebooks or environment dependencies
change.

## Data And Credentials

Do not commit participant lists, credit codes, billing records, sponsor data,
credentials, license files, or private installers.

See [deployment-security.md](deployment-security.md) for security requirements.
