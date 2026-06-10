# Brev Deployment

Brev is the hosted compute option for workshop sessions that need the full
preinstalled environment.

## How It Works

```text
GitHub repository -> GitHub Actions -> GHCR image -> Brev launchable -> participant workspace
```

- The repository stores workshop materials, environment files, and validation scripts.
- GitHub Actions validates changes and publishes the workshop image.
- The Brev launchable starts from the published GHCR image and Docker Compose setup.
- Participants receive NVIDIA credit codes and launchable access instructions through workshop channels.
- Participants create and manage their own Brev workspace from the launchable.

For participant-facing steps (launch workspace, connect IDE, browser Jupyter,
GUI desktop, pause/resume, save work), point participants to
[participant-quickstart.md](participant-quickstart.md).

## Launchable Requirements

The participant launchable should use the prebuilt image path:

- Repository: `https://github.com/quantum-device-consortium/qdw26-workshop-materials`
- Mode: Docker Compose
- Compose file: `compose.deploy.yaml`
- Image: `ghcr.io/quantum-device-consortium/qdw-workshop-materials:main`
- Exposed ports: `8888` (JupyterLab) and `6080` (noVNC web desktop, `/vnc.html`)

The launchable must expose ports `8888` and `6080`. Both services auto-start
inside the container (`compose.deploy.yaml` runs `scripts/start-services.sh`
under supervisor) — there is no manual Jupyter start to configure.

Do not rebuild the image during participant startup. Use the GHCR image built
from `main`, then start the environment with Compose.

If the launchable must use a setup script, use:

```bash
bash scripts/brev-setup.sh
```

The setup script defaults to `compose.deploy.yaml`, runs `docker compose pull`,
starts the service with `docker compose up -d --no-build`, and runs the smoke
check unless `QDW_RUN_SMOKE=0` is set.

`compose.deploy.yaml` starts the workshop container service, which auto-starts
both JupyterLab (port `8888`, tokenless by default) and the noVNC web desktop
(port `6080`, `/vnc.html`). The launchable only needs to expose ports `8888` and
`6080`; no one-click JupyterLab command or manual start is required. Terminal,
SSH, and editor access remain available to the workspace user. Published ports
bind to `${QDW_BIND:-127.0.0.1}` and are reached through Brev's authenticated
proxy.

Existing workspaces do not automatically receive repository or image updates.
Final workshop testing should use a fresh workspace created from the launchable.

## Participant Operating Rules

Participants should:

1. Create one workspace from the workshop launchable.
2. Start or resume the workspace for scheduled workshop sessions.
3. Save notebooks and important outputs before leaving a session.
4. Stop the workspace when not actively using it.
5. Delete the workspace only after the workshop is complete and any needed files have been saved elsewhere.

Stopping is the expected cost-control action between sessions. Deleting is a
cleanup action and should not be used for routine breaks.

See [workspace-persistence.md](workspace-persistence.md) for attendee-facing
stop/start and state-preservation guidance.

## Fast Start Commands

Run inside the workspace repository checkout:

```bash
cd ~/qdw26-workshop-materials
docker compose -f compose.deploy.yaml pull
docker compose -f compose.deploy.yaml up -d --no-build
docker compose -f compose.deploy.yaml exec -T dev python scripts/smoke_environment.py
```

For a normal same-day resume where the environment was already pulled and no
organizer has announced an image update:

```bash
cd ~/qdw26-workshop-materials
QDW_PULL_IMAGE=0 bash scripts/brev-setup.sh
```

Use `QDW_RUN_SMOKE=0` only when an organizer asks participants to skip the smoke
check.

## Release Checklist

Before distributing participant instructions:

1. Merge workshop updates through pull requests.
2. Confirm GitHub Actions passes on `main`.
3. Confirm the GHCR image publish workflow succeeds.
4. Confirm the launchable uses `compose.deploy.yaml` and the GHCR image.
5. Create a fresh Brev test workspace from the launchable.
6. Run the smoke checks below.
7. Run the workshop execution check inside the published image.
8. Verify JupyterLab (port `8888`) and the noVNC web desktop (port `6080`)
   auto-start and are reachable, and that a pause→resume cycle brings both
   services back automatically.
9. Verify stop/start behavior for the selected Brev provider and workspace configuration.
10. Confirm credit-code distribution, support plan, and participant stop reminders.

## Smoke Checks

Run these inside a fresh Brev workspace:

```bash
cd ~/qdw26-workshop-materials
docker compose -f compose.deploy.yaml ps
docker compose -f compose.deploy.yaml exec -T dev python scripts/smoke_environment.py
docker compose -f compose.deploy.yaml exec -T dev python scripts/validate_workshops.py
docker compose -f compose.deploy.yaml exec -T dev python scripts/check_notebooks.py
```

For release validation, also run the manifest-declared attendee notebooks and
Python scripts:

```bash
docker compose -f compose.deploy.yaml exec -T dev python scripts/run_workshop_execution.py
```

Run the checks again whenever workshop notebooks or environment dependencies
change.

## Brev Command Notes

Brev CLI help documents these participant-relevant commands:

- `brev stop` stops a running machine.
- `brev start` starts a paused or off machine, or creates one from a URL.
- `brev delete` is a separate command for deleting an instance.
- Brev CLI help notes that start/stop support is provider-dependent.

Official persistence guarantees for the final NVIDIA/Brev event configuration
should be verified before publishing participant instructions. Until then,
state preservation guidance should be written conservatively.

## Data And Credentials

Do not commit participant lists, credit codes, billing records, sponsor data,
credentials, license files, or private installers.

See [deployment-security.md](deployment-security.md) for security requirements.
