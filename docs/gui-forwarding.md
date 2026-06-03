# GUI Forwarding

Most workshop activities work through JupyterLab, VS Code/Cursor, SSH
terminals, and headless commands. GUI forwarding is optional and is mainly for
desktop applications such as ParaView, KLayout, or Qt-based Quantum Metal
tools.

If a GUI is not required, prefer the headless paths:

```bash
pvpython --version
pvbatch --version
python scripts/smoke_environment.py
```

The `paraview` GUI executable is installed in the image, but it needs a display server. In a plain SSH, Docker, or Brev terminal, running `paraview` without display forwarding will usually fail with a Qt or `xcb` display error.

## What Has To Be Connected

GUI forwarding has three pieces:

- Local display server: software on your laptop that can show Linux GUI windows.
- SSH or Docker display forwarding: a path from the container to that local display server.
- Container environment variables: usually `DISPLAY`, and sometimes Xauthority settings.

For participants, this is an advanced optional setup. Workshop leads should test
it before relying on it during live sessions.

## macOS With XQuartz

Install and start XQuartz on the Mac:

```bash
brew install --cask xquartz
open -a XQuartz
```

In XQuartz settings, enable network client connections, then restart XQuartz.

Allow local Docker containers to connect to XQuartz:

```bash
xhost +127.0.0.1
xhost +localhost
```

Start the workshop container and pass a display value when launching GUI commands:

```bash
docker compose up -d --build
docker compose exec -e DISPLAY=host.docker.internal:0 dev paraview
```

For the published image:

```bash
docker compose -f compose.deploy.yaml up -d
docker compose -f compose.deploy.yaml exec -e DISPLAY=host.docker.internal:0 dev paraview
```

When finished, you can remove the temporary XQuartz access:

```bash
xhost -127.0.0.1
xhost -localhost
```

## Linux Desktop With X11

On a Linux laptop using X11, Docker can usually share the host X11 socket.

Allow local Docker connections:

```bash
xhost +local:docker
```

Start the container with the X11 socket mounted:

```bash
docker compose run --rm \
  -e DISPLAY="$DISPLAY" \
  -e QT_X11_NO_MITSHM=1 \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  dev paraview
```

For an already-running container, the X11 socket must have been mounted when the container was created. If it was not, stop and recreate the container with the socket mount.

When finished:

```bash
xhost -local:docker
```

## Windows With VcXsrv Or X410

Install and start an X server such as VcXsrv or X410.

For VcXsrv, common settings are:

- Multiple windows
- Start no client
- Disable access control only on trusted/private networks, and rely on Windows Firewall to restrict access to private networks

Then start the container and point `DISPLAY` at the Windows host:

```powershell
docker compose up -d --build
docker compose exec -e DISPLAY=host.docker.internal:0 dev paraview
```

If Windows Firewall prompts you, allow the X server on private networks only.

## Remote Hosts And Brev

For remote Docker hosts, there are two supported patterns.

### Preferred: Use Headless Tools Remotely

Use JupyterLab, VS Code/Cursor remote access, SSH terminals, `pvpython`, and `pvbatch`. This is more reliable for workshop-scale use and avoids local display setup.

### Advanced: SSH X11 Forwarding

If you need a GUI from a remote host, your laptop must run a display server and your SSH connection must enable trusted X11 forwarding:

```bash
ssh -Y user@remote-host
echo "$DISPLAY"
```

Then the container must be able to reach the SSH-forwarded display on the remote
host. On Linux remote hosts this may require host networking or an
Xauthority/socket mount. Because providers differ, workshop staff should test
the exact Brev image and instance type before publishing GUI-forwarding
instructions.

If this is not pre-tested, do not depend on GUI forwarding during a live workshop.

## Quick Test

Use these commands in order:

```bash
echo "$DISPLAY"
docker compose exec dev sh -lc 'echo "$DISPLAY"'
docker compose exec dev pvpython --version
docker compose exec dev pvbatch --version
docker compose exec dev paraview
```

If `pvpython` and `pvbatch` work but `paraview` fails, the image is probably fine and the issue is display forwarding.

## Troubleshooting

- `qt.qpa.xcb: could not connect to display`: the container cannot reach your display server.
- `Could not load the Qt platform plugin "xcb"`: display forwarding or required Qt/X11 libraries are missing.
- Window opens but is blank or slow: try a local wired network, avoid VPNs, or use Jupyter/headless tools instead.
- Remote GUI over SSH is laggy: this is expected for 3D applications; use `pvpython`, `pvbatch`, or download output files for local visualization.
- Security warning about `xhost`: only allow access on trusted networks, and revoke access when done.
