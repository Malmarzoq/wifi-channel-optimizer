# Choose a run mode

Complete the repository setup and configure `.env` before using either mode. Use **one mode at a time**: never run `main.py` manually while the systemd service is active.

## Path 1: Run manually

Choose this for testing, demonstrations, or when you want the agent to run only while a terminal is open.

Start it from the project directory:

```bash
.venv/bin/python main.py
```

The terminal displays the agent output. Stop it with `Ctrl+C` in that same terminal.

Manual mode does not survive closing the terminal or restarting the computer. If the automatic service was previously enabled, stop and disable it before starting manual mode:

```bash
sudo systemctl disable --now wifi-channel-optimizer.service
```

## Path 2: Start automatically after every reboot

Choose this for normal, unattended operation. Install and enable the service once from the project directory:

```bash
./scripts/install-systemd-service.sh
```

The script starts the agent now and enables it to start automatically after every restart. It reads settings from the local `.env` file; it does not copy router credentials into the systemd unit.

Check whether it is running:

```bash
systemctl status wifi-channel-optimizer.service
```

Watch its live output without starting a second agent:

```bash
journalctl -u wifi-channel-optimizer.service -f
```

To stop it now and prevent automatic startup after future reboots:

```bash
sudo systemctl disable --now wifi-channel-optimizer.service
```

To turn automatic operation back on and start it immediately:

```bash
sudo systemctl enable --now wifi-channel-optimizer.service
```
