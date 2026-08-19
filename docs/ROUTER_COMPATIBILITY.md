# Router compatibility

Compatibility is determined by the router's firmware capabilities, not by its model name alone. A router is supported only after its own configuration passes the checks below. Do not describe an untested model or firmware version as compatible.

## Required capabilities

The router must provide all of the following over an SSH connection on the LAN:

- A configured SSH service and a known, trusted host key.
- The Broadcom `wl` command, including `channel`, `scan`, `scanresults`, and `counters` for the 2.4 GHz interface.
- The `nvram` command for the configured radio name.
- Permission for the SSH account to run these commands and, when `DRY_RUN=false`, to restart wireless service.

The agent cannot support routers that expose only a web interface, use a non-Broadcom wireless CLI, or do not allow these commands over SSH.

## Verified configuration

| Router | Status | Notes |
| --- | --- | --- |
| ASUS ROG Rapture GT-AX11000 Pro | Verified by the maintainer on their own configuration | The 2.4 GHz interface was `eth6`; this is not a universal ASUS value. Re-run the checks below after every firmware change. |

This entry verifies the maintainer's configuration, not every GT-AX11000 Pro or every ASUS firmware release.

## SSH setup and port

Set SSH to **LAN only** whenever possible. ASUS documents the setting at **Administration > System > Service > Enable SSH**; see the [official ASUS SSH instructions](https://www.asus.com/support/faq/1048201/). The project uses port `22` by default, but a router configured on another port is supported through `.env`:

```dotenv
SSH_PORT=22
```

Replace `22` with the port configured on the router. Never expose the router SSH service to the internet merely for this agent.

## Find and verify the 2.4 GHz interface

`WIFI_IFACE` is the radio interface passed to `wl`. It differs between models and firmware versions. `eth6` is the value verified on the maintainer's GT-AX11000 Pro; it is only an example in `.env.example`.

Before running the agent, use a trusted LAN connection to run this read-only check. Replace every placeholder with the intended values:

```bash
ssh -p <ssh-port> <router-user>@<router-ip> \
  'wl -i <2.4-interface> channel; wl -i <2.4-interface> counters; nvram get <radio>_channel'
```

The command must return a channel and counters without an error. Then configure the matching values in `.env`:

```dotenv
SSH_PORT=<ssh-port>
WIFI_IFACE=<2.4-interface>
NVRAM_RADIO=<radio>
DRY_RUN=true
```

Run the agent in dry-run mode first. It performs its normal reads and scan but never changes the router channel. Turn off dry-run only after the output is correct and you have a rollback plan.
