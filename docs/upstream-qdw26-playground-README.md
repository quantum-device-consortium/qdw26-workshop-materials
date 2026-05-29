# QDW 2026 Playground

A pre-configured environment for tutorials at the Quantum Device Workshop 2026.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with the [Compose plugin](https://docs.docker.com/compose/install/) (`docker compose version`)
- For local development, clone this repo so the Compose file can bind-mount the project directory

## Local Docker

The image installs **uv**, a managed Python, **Palace** (via a custom [base image](https://hub.docker.com/repository/docker/abhishekchak52/palace_env/general) ), and locked dependencies from `pyproject.toml` / `uv.lock`. Application source is **not** copied into the image at build time; you mount the repo at runtime (see [compose.yaml](compose.yaml)).


### Build and start the dev container

From the repository root:

```bash
docker compose up --build
```

This builds the image (if needed), bind-mounts the current directory to `/home/ubuntu/qdw26-playground`, sets `QISKIT_METAL_HEADLESS=1`, runs `uv sync --locked`, then keeps the container alive (`sleep infinity`) so you can exec into it.

### Run commands in the container

Here are some simple things to test that Quantum Metal and Palace are installed in the container. With the stack running in another terminal:

```bash
docker compose exec dev uv run python main.py
docker compose exec dev palace --version
docker compose exec dev bash
```

One-off run without leaving a long-lived service up:

```bash
docker compose run --rm dev sh -c "uv sync --locked && uv run python main.py"
```

### Build or push without Compose

```bash
docker build -t abhishekchak52/qdw26-playground:latest .
docker push abhishekchak52/qdw26-playground:latest
```

Use your own registry/username if you want to incorporate your own changes.

### Use a pre-built image (no local build)

```bash
docker compose pull
docker compose up
```

Omit `--build` so Compose only pulls `image:` from the registry.

---

## NVIDIA Brev

Brev can run this repository as a **custom Docker container** so you get the same toolchain (Palace, uv, Qiskit Metal stack) on a cloud GPU instance.

The upstream project used a Brev launchable with a default 16 vCPU / 16 GB
memory instance. For the current workshop environment, use the deployment
guidance in [brev.md](brev.md) rather than the historical upstream launchable.

Open the instance in your editor (for example Cursor):

```bash
brev open <instance-name> cursor
```

This drops you into the host that will run the development container. There is a `workspace` directory, but ignore that for the time being. 

The repository files are available under **`/home/ubuntu/qdw26-playground`**. Enter that directory and start running the development container. 

```bash
cd qdw26-playground
docker compose up -d
```

Then you can attach to the running container for development. Press `Ctrl+Shift+P` (`Cmd+Shift+P` on Mac) then select the `Attach to running container` and connect to the `qdw26-playground-dev-...` container. Once the new window opens, open the `/home/ubuntu/qdw26-playground` folder in this window. Now you're all set to try out the examples!


More help: [NVIDIA Brev documentation](https://docs.nvidia.com/brev/).
