# Access Paths

The attendee environment should be usable from several entry points. None of these paths is the only supported path.

## JupyterLab

Use JupyterLab for notebook-first workshops:

```bash
docker compose -f compose.deploy.yaml exec dev uv run jupyter lab --ip 0.0.0.0 --port 8888 --no-browser
```

Open the URL printed by JupyterLab.

The compose files bind port `8888` to localhost by default. Use Brev's authenticated access or an SSH tunnel for remote access unless the deployment owner intentionally sets `QDW_JUPYTER_BIND=0.0.0.0`.

## VS Code Or Cursor

Use an editor when you want a full project tree, terminals, and notebook support in one place.

1. Start the environment with `docker compose up -d --build`.
2. Attach the editor to the running `dev` container.
3. Open `/home/ubuntu/qdw-workshop-materials`.

## SSH

Use SSH on Brev or another remote host when terminal access is the most direct route:

```bash
cd qdw-workshop-materials
docker compose -f compose.deploy.yaml up -d
docker compose -f compose.deploy.yaml exec dev bash
```

## Local Terminal

Use Docker Compose directly when developing locally:

```bash
docker compose up --build
docker compose exec dev bash
```

All paths use the same repository checkout and shared environment.
