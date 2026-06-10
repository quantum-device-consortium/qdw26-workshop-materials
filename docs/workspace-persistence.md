# Workspace Persistence

Use this guidance for Brev workspaces created from the workshop launchable.

## Stop, Start, And Delete

- Stop the workspace when not in a scheduled workshop session.
- Start the same workspace again for the next session.
- Do not delete the workspace for breaks between sessions.
- Delete the workspace only after the workshop is complete and needed files have been saved elsewhere.

Brev CLI help documents `brev stop` for stopping a running machine and
`brev start` for starting a paused or off machine. The same help notes that
start/stop support is provider-dependent.

## What Should Persist

Stopped workspaces generally preserve disk and workspace state, but the final
event configuration and provider behavior should be verified by organizers
before participant instructions are published.

Participants should not rely on unsaved notebook state, terminal history,
temporary directories, or disposable container layers as the only copy of
important work.

## Save Work Before Stopping

Before stopping a workspace:

1. Save open notebooks.
2. Write important generated outputs under the workspace or repository directory.
3. Download or copy any irreplaceable results needed after the event.
4. Commit and push changes if using Git for personal notes or solutions.
5. Stop the Brev workspace from the Brev UI or with `brev stop`.

Avoid storing important files only in `/tmp` or in a container that may be
recreated by future image updates.

## Resume A Workspace

After a pause/resume or host reboot, nothing needs to be re-run.
`compose.deploy.yaml` sets `restart: unless-stopped`, so the container and both
services — JupyterLab (port `8888`) and the noVNC web desktop (port `6080`) —
come back automatically. Just reopen the port `8888` / `6080` URLs. See
[participant-quickstart.md](participant-quickstart.md) for the participant flow.

The setup script is optional on resume. If you want to explicitly start the
Compose service without re-pulling the image, you can still run:

```bash
cd ~/qdw26-workshop-materials
QDW_PULL_IMAGE=0 bash scripts/brev-setup.sh
```

If the organizers announce an updated workshop image, run the standard setup to
pull it:

```bash
cd ~/qdw26-workshop-materials
bash scripts/brev-setup.sh
```

The standard setup pulls the current GHCR image, starts the service with
`docker compose up -d --no-build`, and runs the smoke check.

## If Something Looks Missing

1. Confirm the same Brev workspace was started.
2. Check the workspace or repository directory first.
3. Check whether files were saved inside a container before it was recreated.
4. Ask workshop support before deleting or recreating the workspace.
