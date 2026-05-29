# Brev

Brev provides the remote workspace that attendees and workshop leads can use
without installing the full toolchain locally. GitHub stores the workshop
materials and Docker build definition. GitHub Container Registry stores the
published workshop image.

The default deployment target is a public GitHub repository plus a public GHCR
image. This lets Brev clone the materials and pull the image without repository
deploy keys or package tokens.

## Launchable Configuration

Expected configuration:

- Source repository: `https://github.com/quantum-device-consortium/qdw26-workshop-materials`
- Container mode: Docker Compose
- Compose file: `compose.yaml`
- Instance type: `n2d-highcpu-16`
- Compute: 16 vCPUs, 16 GiB RAM, CPU-only, GCP
- Storage: 64 GiB
- Visibility: selected according to the event billing and access model
- Community publishing: disabled unless explicitly approved for public use

The launchable is a reusable template. A Brev workspace is the actual machine
created from that template.

## System Overview

Use this dependency chain when deciding what to update or test:

```text
GitHub repo -> GitHub Actions -> GHCR image -> Brev launchable -> Brev workspace
```

- GitHub repo: source of truth for materials, docs, Dockerfile, and Compose.
- GitHub Actions: validates pull requests and publishes images on `main`.
- GHCR image: packaged attendee environment.
- Brev launchable: organizer-managed template for creating workspaces.
- Brev workspace: a running or stopped machine created for workshop use.

## Update Behavior

Pull requests do not update attendee environments by themselves.

After a pull request is merged to `main`:

1. GitHub Actions validates the repository.
2. GitHub Actions publishes `ghcr.io/quantum-device-consortium/qdw-workshop-materials:main`.
3. The same Brev launchable can be used for the next fresh workspace.
4. A fresh workspace should use the current `main` branch and Compose setup.

Existing Brev workspaces do not update automatically. They should either be
deleted and recreated from the launchable, or manually updated with `git pull`
and a Docker Compose rebuild/pull. For attendee support, prefer fresh
workspaces so everyone starts from the same known state.

The default attendee experience should use organizer-prepared workspaces.
Attendees should not need to select hardware, edit launchable settings, or
manage Docker startup unless the workshop explicitly chooses a self-service
deployment model.

## Release Flow

Release checklist:

1. Workshop lead opens a pull request.
2. Maintainers review the materials and dependency requests.
3. GitHub Actions checks must pass.
4. Merge into `main`.
5. Confirm the image publish workflow succeeds.
6. Deploy one fresh Brev workspace from the launchable.
7. Run the Brev smoke checks below.
8. Verify the supported access paths: terminal, SSH, VS Code/Cursor,
   JupyterLab, and optional GUI forwarding.
9. Stop or delete the test workspace.
10. Publish or reaffirm attendee access instructions.

Do not treat green CI alone as a final attendee-readiness signal. Always test
one fresh Brev workspace after major environment or workshop-material changes.

## Billing Guardrails

Before creating attendee workspaces, document which account pays for them.
Attendee-facing access should have an explicit billing account, credit pool,
and access control model.

Use one of these approved patterns for attendee access:

- Sponsored workshop org: organizers create workspaces in a dedicated workshop
  billing account or credit-backed organization managed for the event.
- Organizer-provisioned workspaces: organizers create and monitor a controlled
  number of workspaces, then distribute access according to the workshop plan.
- Bring-your-own-Brev account: only if attendees are explicitly expected to use
  their own credits or billing account.

Use attendee self-deployment only when the billing behavior and
organizer-approved access model are documented.

## Cost Check

Before provisioning, check available instance types and pricing:

```bash
brev search cpu --json
brev search gpu --json
```

Use a low-cost or credited instance for setup testing. Larger instances can be selected later for attendee load.

Do not start or create instances until there is a clear test window and shutdown plan.

Stopped workspaces may still accrue storage cost. Delete test workspaces when
they do not contain work that needs to be preserved.

## Secure Access

For the current public-repo/public-image mode, Brev should not need GitHub
credentials to clone the repository or pull the image.

Before making a launchable attendee-facing, verify both assumptions from a
machine that is not logged in to GHCR:

```bash
git ls-remote https://github.com/quantum-device-consortium/qdw26-workshop-materials.git HEAD

tmpdir="$(mktemp -d)"
DOCKER_CONFIG="$tmpdir" docker manifest inspect ghcr.io/quantum-device-consortium/qdw-workshop-materials:main
rm -rf "$tmpdir"
```

If the repository is made private again later, use a read-only deploy key
scoped only to this repository. A fine-grained GitHub token can also work for
repository cloning, but it should be limited to repository read access.

If the GHCR image is private, Brev needs package read access for the pull.
Prefer a short-lived token or Brev secret mechanism if available.

Do not put long-lived credentials in notebooks, committed files, shell history, or attendee-facing docs.

`scripts/brev-clone-and-setup.sh` loads GitHub SSH host keys from GitHub's HTTPS metadata endpoint before cloning. This avoids blindly trusting an unverified first SSH connection. The script fails closed if `curl` or `python3` are unavailable.

See [deployment-security.md](deployment-security.md) before sharing any attendee-facing environment.

For GHCR, `scripts/brev-setup.sh` supports these environment variables:

```bash
GHCR_USERNAME=<github-username>
GHCR_TOKEN=<classic-token-with-read-packages>
```

If those are not set, the script assumes Docker is already authenticated or the image is public.

When GHCR credentials are supplied, the setup script uses a temporary Docker config directory and removes it before exiting so package tokens are not left in the default Docker config.

## Deployment Modes

Local development uses `compose.yaml` and may build from source:

```bash
docker compose up -d --build
```

Brev deployment uses `compose.deploy.yaml` and pulls the published image:

```bash
docker compose -f compose.deploy.yaml pull
docker compose -f compose.deploy.yaml up -d
docker compose -f compose.deploy.yaml exec -T dev python scripts/smoke_environment.py
```

Use the deployment compose file for attendee-facing environments. Use the local compose file when changing dependencies or debugging Docker builds.

By default, the deployment compose file binds Jupyter to `127.0.0.1:8888`. Set `QDW_JUPYTER_BIND=0.0.0.0` only if Brev's access layer requires a public interface and the instance is protected by authentication.

## Start A Test Workspace From The Launchable

Only run this after confirming the cost, account, and shutdown plan.

1. Open the staging launchable.
2. Confirm it shows Docker Compose mode.
3. Confirm the instance type and storage are acceptable.
4. Deploy a test workspace.
5. Wait for the workspace build/startup to finish.

Open the instance using the path that fits the workshop:

```bash
brev open qdw-workshop-materials
brev open qdw-workshop-materials code
brev open qdw-workshop-materials cursor
```

SSH is also supported through the Brev CLI.

## Brev Smoke Checks

After logging into a fresh Brev workspace, run:

```bash
cd qdw-workshop-materials
docker compose ps
docker compose exec dev python scripts/smoke_environment.py
docker compose exec dev python scripts/validate_workshops.py
docker compose exec dev python scripts/check_notebooks.py
```

If using the deployment compose file for a specific test, run the equivalent
commands with `-f compose.deploy.yaml`.

Also verify the user-facing access paths that the workshop will advertise:

```text
terminal
SSH
VS Code or Cursor
JupyterLab
GUI forwarding, when needed
```

JupyterLab, editor attachment, SSH, and terminal access all use the same
repository checkout and shared environment.

## Shutdown

After a test, stop or delete the instance so credits are not consumed by idle
compute. Delete only when the instance does not contain work that needs to be
preserved. For short-lived release tests, deletion is preferred because stopped
workspace storage can still accrue cost.
