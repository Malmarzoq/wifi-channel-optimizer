#!/usr/bin/env bash
# Install this repository as a per-user systemd service. Run as the account
# that owns the checkout; the script requests sudo only to install the unit.

set -eu

SERVICE_NAME="wifi-channel-optimizer.service"
SERVICE_USER="$(id -un)"
PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)"
UNIT_DESTINATION="/etc/systemd/system/$SERVICE_NAME"

if [ "$(id -u)" -eq 0 ]; then
    echo "Run this script as the project owner, without sudo."
    exit 1
fi

if [ ! -x "$PROJECT_DIR/.venv/bin/python" ]; then
    echo "Missing virtual environment: $PROJECT_DIR/.venv/bin/python"
    echo "Create it and install dependencies before installing the service."
    exit 1
fi

temporary_unit="$(mktemp)"
trap 'rm -f "$temporary_unit"' EXIT

cat >"$temporary_unit" <<EOF
[Unit]
Description=Wi-Fi Channel Optimizer
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$PROJECT_DIR
Environment=PYTHONUNBUFFERED=1
ExecStart=$PROJECT_DIR/.venv/bin/python $PROJECT_DIR/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo install -m 644 "$temporary_unit" "$UNIT_DESTINATION"
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"
sudo systemctl status --no-pager "$SERVICE_NAME"
