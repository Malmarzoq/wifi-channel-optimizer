# Wi-Fi Channel Optimizer

An autonomous Python agent that scans 2.4 GHz Wi-Fi interference and selects a better router channel over SSH.

> Designed for routers whose firmware exposes the Broadcom `wl` and `nvram` commands over SSH. Review the commands for your router before using it on a production network.

## Features

- Scans nearby access points across channels 1–13.
- Scores interference using channel overlap and signal strength.
- Switches channels only when the predicted improvement is significant.
- Verifies transmission retries and rolls back after degradation.

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
WIFI_IFACE=eth6
SSH_KNOWN_HOSTS=
```

Before running the agent, verify the router's SSH fingerprint and add it to `known_hosts`:

```bash
ssh-keyscan -H 192.168.1.1 >> ~/.ssh/known_hosts
```

## Run

```bash
python main.py
```

## Security

- `.env`, log files, and `config/secrets.py` are ignored by Git.
- SSH host keys are verified; unknown hosts are rejected.
- Use a dedicated router account with only the permissions this agent needs.

## License
