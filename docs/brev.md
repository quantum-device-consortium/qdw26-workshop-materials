# Brev

Brev hosts the remote compute instance. GitHub stores the workshop materials and Docker build definition. GitHub Container Registry stores the published workshop image.

The preferred deployment path is:

1. Merge workshop updates into `main`.
2. Let GitHub Actions validate and publish `ghcr.io/quantum-device-consortium/qdw-workshop-materials:main`.
3. Start a Brev instance only after checks are green.
4. Clone this repository onto the Brev instance.
5. Run `scripts/brev-setup.sh`, which pulls the published image through `compose.deploy.yaml`.

This keeps Brev deployment close to what CI already tested.

## Cost Check

Before provisioning, check available instance types and pricing:

```bash
brev search cpu --json
brev search gpu --json
```

Use a low-cost or credited instance for setup testing. Larger instances can be selected later for attendee load.

Do not start or create instances until there is a clear test window and shutdown plan.

## Secure Access

The Brev instance may need two read-only credentials:

- GitHub repository access for cloning this private repository.
- GHCR package access for pulling the private image, if the package is not public.

Recommended repository access is a read-only deploy key scoped only to this repository. A fine-grained GitHub token can also work for repository cloning, but it should be limited to repository read access.

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

## Start A Test Workspace

Only run this after confirming the cost and instance type. A small CPU instance is enough for first validation:

```bash
brev create qdw-workshop-materials \
  --type cpu-d3.4vcpu-16gb \
  --startup-script @scripts/brev-clone-and-setup.sh
```

Open the instance using the path that fits the workshop:

```bash
brev open qdw-workshop-materials
brev open qdw-workshop-materials code
brev open qdw-workshop-materials cursor
```

SSH is also supported through the Brev CLI.

## After Login

```bash
cd qdw-workshop-materials
docker compose -f compose.deploy.yaml ps
docker compose -f compose.deploy.yaml exec dev bash
```

JupyterLab, editor attachment, SSH, and terminal access all use the same running environment.

## Shutdown

After a test, stop or delete the instance so credits are not consumed by idle compute. Delete only when the instance does not contain work that needs to be preserved.
