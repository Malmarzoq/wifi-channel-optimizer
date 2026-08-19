# Architecture

## Scope

Wi-Fi Channel Optimizer is a closed-loop Python agent for compatible 2.4 GHz routers. It observes nearby Wi-Fi activity, estimates channel interference, applies a channel change only when it is worthwhile, and verifies the result before keeping it.

The project expects router firmware that provides the Broadcom `wl` and `nvram` commands over SSH. Those commands are device-specific: inspect and adapt them for your router before running the agent on a live network.

## Components

| Component | Responsibility |
| --- | --- |
| `config/settings.py` | Loads local environment settings and defines timing and safety thresholds. |
| `tools/router_tools.py` | Connects to the router, scans Wi-Fi data, reads counters, and applies channel changes. |
| `memory/state_memory.py` | Keeps recent decisions and enforces the cooldown period. |
| `core/agent.py` | Evaluates interference, makes the switching decision, and coordinates verification or rollback. |
| `main.py` | Runs the agent continuously and writes operational logs. |

## Decision flow

1. Read the router's current channel.
2. Request a Wi-Fi scan and collect nearby access-point signal data.
3. Score channels 1–13 using signal strength and channel-overlap weights.
4. Select the channel with the lowest score.
5. Keep the current channel when it is already best, the cooldown is active, or the predicted improvement is below the configured threshold.
6. Record transmission counters, apply the new channel, then wait for the verification period.
7. Read counters again. If retry growth exceeds the configured threshold, restore the prior channel.

## Safety controls

- **Improvement threshold:** prevents changes that offer too little benefit.
- **Cooldown:** prevents repeated switching and gives connected clients time to settle.
- **Post-change verification:** checks transmission retries after a change.
- **Automatic rollback:** restores the previous channel after a harmful retry increase.
- **SSH host-key verification:** rejects unknown router hosts rather than trusting them automatically.

## Configuration

Configuration is read from a local `.env` file. Copy `.env.example`, set values that match your local network, and keep `.env` out of version control.

The principal settings are:

| Setting | Purpose |
| --- | --- |
| `ROUTER_IP` | Router address on the local network. |
| `ROUTER_USER` / `ROUTER_PASS` | Dedicated router credentials used for SSH. |
| `WIFI_IFACE` | Router interface to manage. |
| `SSH_KNOWN_HOSTS` | Optional path to a dedicated trusted-hosts file. |
| `CHECK_INTERVAL_SECONDS` | Delay between evaluation cycles. |
| `COOLDOWN_MINUTES` | Minimum interval between successful channel changes. |
| `VERIFICATION_DELAY` | Wait time before post-change verification. |
| `TX_RETRIES_ABORT_THRESHOLD` | Retry increase that triggers a rollback. |

## Operational limits

- The agent currently targets the 2.4 GHz band and channels 1–13.
- Router command syntax and counter formats vary by firmware.
- A channel change can briefly interrupt connected clients; validate the behavior in a controlled environment first.
- The in-memory decision history is reset when the process restarts.
