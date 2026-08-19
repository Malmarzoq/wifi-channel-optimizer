# Running as a systemd service

Use systemd when the agent should start automatically and restart after an unexpected failure. Complete the setup and SSH host-key verification in the main README before enabling this service.

## Prepare the application

Replace `<project-dir>` and `<service-user>` below with your own values. Keep the project directory writable by the service user, but do not run the service as `root`.

```bash
cd <project-dir>
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
chmod 600 .env
```

Add the router host key to the service user's `known_hosts` file, or set `SSH_KNOWN_HOSTS` in `.env` to a dedicated file that the service user can read. Verify the fingerprint through a trusted channel before accepting it.

## Fast installation

This repository includes a reusable [unit-file template](../deploy/wifi-channel-optimizer.service.template) and an installation script. From the project directory, run the script as the account that owns the checkout (do not prefix it with `sudo`):

```bash
./scripts/install-systemd-service.sh
```

It detects the project directory and your user name, asks for `sudo` only to install the unit file, enables the service, and starts it. It reads router settings from the local `.env` file; credentials are never placed in the systemd unit.

## Create the unit file

Create `/etc/systemd/system/wifi-channel-optimizer.service` with the following content, replacing both placeholders:

```ini
[Unit]
Description=Wi-Fi Channel Optimizer
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=<service-user>
WorkingDirectory=<project-dir>
Environment=PYTHONUNBUFFERED=1
ExecStart=<project-dir>/.venv/bin/python <project-dir>/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Enable and monitor

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now wifi-channel-optimizer.service
sudo systemctl status wifi-channel-optimizer.service
```

Follow its logs with:

```bash
journalctl -u wifi-channel-optimizer.service -f
```

To stop it later:

```bash
sudo systemctl disable --now wifi-channel-optimizer.service
```

## Avoid duplicate agents

Do not run `main.py` manually while `wifi-channel-optimizer.service` is active. Two agents can read the same router state and make competing channel decisions.

Use `journalctl -u wifi-channel-optimizer.service -f` to watch the active service instead.

## Updating safely

1. Stop the service.
2. Fetch the new release or commit.
3. Install any updated dependencies in the virtual environment.
4. Review `.env` and verify the router host key is still correct.
5. Start the service and monitor the first evaluation cycle.

Do not treat an automated restart as a substitute for reviewing router behavior after an upgrade.
