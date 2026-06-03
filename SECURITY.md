# Security Policy

## Reporting

Report security issues privately to the repository maintainers or workshop
organizers. Do not open a public issue for secrets, credential exposure,
access-control problems, or vulnerabilities that could affect participants.

## Supported Deployment

The supported hosted deployment path is:

- GitHub Actions validates the repository.
- GitHub Actions publishes the image to GHCR.
- Brev pulls the published image with `compose.deploy.yaml`.
- Participants access the environment through approved Brev, JupyterLab,
  editor, SSH, or terminal paths.

Do not add secrets, private keys, license files, package tokens, or cloud credentials to the repository or Docker image.

## Dependency Review

Dependency updates should keep `pyproject.toml` and `uv.lock` synchronized and should pass local validation plus GitHub Actions before deployment.
