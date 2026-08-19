# Wi-Fi Channel Optimizer

An autonomous Python agent that scans 2.4 GHz Wi-Fi interference and selects a better router channel over SSH.

> Designed for routers whose firmware exposes the Broadcom `wl` and `nvram` commands over SSH. Review the commands for your router before using it on a production network.

## Features

- Scans nearby access points across channels 1–13.
- Scores interference using channel overlap and signal strength.
- Switches channels only when the predicted improvement is significant.
- Verifies transmission retries and rolls back after degradation.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Run as a systemd service](docs/SYSTEMD.md)
- [Router compatibility](docs/ROUTER_COMPATIBILITY.md)

## Requirements

- Python 3.9 or later
- SSH access to a compatible router
- The router's SSH host key saved in `known_hosts`

## Setup

```bash
git clone https://github.com/Malmarzoq/wifi-channel-optimizer.git
cd wifi-channel-optimizer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set your local router credentials in `.env`; never commit this file.

```dotenv
ROUTER_IP=192.168.1.1
ROUTER_USER=your_router_username
ROUTER_PASS=your_router_password
SSH_PORT=22
# `eth6` is an example from a tested ASUS configuration; verify yours first.
WIFI_IFACE=eth6
SSH_KNOWN_HOSTS=
```

Obtain the router's SSH fingerprint through a trusted channel. Only after comparing it should you add the key to `known_hosts`:

```bash
ssh-keyscan -p <ssh-port> -H <router-ip> >> ~/.ssh/known_hosts
```

## Run

Choose one mode at a time. See [run modes](docs/RUN_MODES.md) for the complete start, stop, and switching instructions.

### Path 1: Run manually

Choose this for testing or demonstrations. It stops when you press `Ctrl+C`, close the terminal, or restart the computer.

From the project directory, run:

```bash
cd wifi-channel-optimizer
.venv/bin/python main.py
```

To stop a manual run, press `Ctrl+C` in the same terminal.

From another terminal, watch the manual agent's live log with:

```bash
tail -f wifi_agent.log
```

This follows the log only; `Ctrl+C` stops the display, not the agent. To check whether a manual agent is running:

```bash
pgrep -af 'python.*main.py'
```

If you previously enabled the automatic service, disable it before using manual mode.


> Do not start a manual run while the systemd service is active. That would create two agents that can make competing channel decisions. If the service is active, follow its output with `journalctl -u wifi-channel-optimizer.service -f` instead.

### Path 2: Run automatically after every restart

Choose this for normal unattended operation. Install and start the service once:

```bash
./scripts/install-systemd-service.sh
```

The service starts now and starts again automatically after every reboot.

To stop and disable that service later:

```bash
sudo systemctl disable --now wifi-channel-optimizer.service
```

This stops it now and prevents automatic startup after future reboots. To turn automatic operation back on and start it immediately:

```bash
sudo systemctl enable --now wifi-channel-optimizer.service
```

Check its status with:

```bash
systemctl status wifi-channel-optimizer.service
```

Watch its live output without starting another agent:

```bash
journalctl -u wifi-channel-optimizer.service -f
```

See the [systemd guide](docs/SYSTEMD.md) for the service template and advanced setup.

## Security

- `.env`, log files, and `config/secrets.py` are ignored by Git.
- SSH host keys are verified; unknown hosts are rejected.
- Use a dedicated router account with only the permissions this agent needs.

## License
