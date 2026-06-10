## Summary

-

## Workshop Impact

- Workshop folder touched:
- Entry notebooks changed:
- Dependency requests changed:

## Checks

- [ ] `python scripts/validate_workshops.py`
- [ ] `python scripts/check_notebooks.py`
- [ ] `bash -n scripts/*.sh`
- [ ] `docker compose config`
- [ ] `docker compose -f compose.deploy.yaml config`
- [ ] Docker image smoke test, if Docker is available locally
- [ ] Workshop execution test, if Docker is available locally:
      `docker run --rm qdw-workshop-materials:local python scripts/run_workshop_execution.py`

## Access Paths Considered

- [ ] JupyterLab
- [ ] VS Code or Cursor
- [ ] SSH or terminal
