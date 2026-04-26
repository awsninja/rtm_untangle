# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RTM Untangle is a Python daemon that ties [Remember the Milk](https://www.rememberthemilk.com/) task completion to internet access controls and productivity enforcement. It:
- Monitors RTM for overdue tasks
- Controls an Untangle firewall to restrict/allow internet access for child accounts
- Locks/unlocks child user accounts via SSH based on task status and time of day
- Enforces productivity mode on the owner's workstation when focus tasks are overdue

## Running the App

```bash
# Via Docker Compose (primary deployment method)
docker-compose up -d

# Build Docker image
docker build -t untangle:latest .

# Run directly with Python
pip install -r requirements.txt
cp .env.sample .env  # then fill in credentials
python poll.py
```

There are no tests or linting configs in this project.

## Architecture

**Entry point:** `poll.py` — runs an infinite loop with randomized 30–90 minute sleep intervals, calling `kids_routine()` and `self_routine()` each iteration.

**Core modules:**
- `rtm.py` — RTM API client; `poll()` checks for overdue tasks, `poll_focus()` checks focus tasks
- `unifi.py` — Unifi controller client using `pyunifi`; `firewall_start()` blocks all configured MACs, `firewall_stop()` unblocks them. Maintains internal state (`RUNNING`/`INITIALIZED`) since status is not re-queried from the controller.
- `kids.py` — Decision logic for locking child accounts; implements chaos monkey (1-in-10 random enforcement), nighttime lockout (10 PM–4 AM always locks), and task-based lockout
- `self_routine.py` — Productivity enforcement for the owner's workstation; calls `./productivity_on` or `./productivity_off` remotely via SSH
- `ssh.py` — Paramiko-based SSH utility; loads RSA key from `./ssh_private_key`, executes commands on remote hosts

**Lock/unlock flow:** When the firewall starts, `kids.py` blocks the child's MAC addresses on the Unifi router, then SSHes to child accounts and runs `passwd -l` (lock password), screen lock commands, and kills user sessions. On firewall stop, it unblocks MACs and runs `passwd -u` (unlock).

**MAC address config:** Each account in `accounts.json` has a `macs` list — add all device MAC addresses (phone, tablet, PC, etc.) for each child. The Unifi controller blocks these at Layer 2.

**Configuration:**
- `accounts.json` — maps hostnames to usernames for child accounts (`accounts`) and owner's workstation (`productivity_accounts`)
- `.env` — RTM credentials, Untangle server address/firewall ID, poll intervals, chaos monkey ratio, RTM task filters
- `.env.sample` — documents all required environment variables

## Key Environment Variables

| Variable | Purpose |
|---|---|
| `RTM_API_KEY`, `RTM_SHARED_SECRET`, `RTM_TOKEN` | RTM authentication |
| `UNIFI_SERVER_ADDRESS`, `UNIFI_PORT`, `UNIFI_USERNAME`, `UNIFI_PASSWORD`, `UNIFI_SITE` | Unifi controller credentials (port defaults to 8443; site defaults to `default`) |
| `OVERDUE_TASK_FILTER` | RTM filter string for kids overdue tasks |
| `POLL_INTERVAL_MIN` / `POLL_INTERVAL_MAX` | Sleep range in seconds (default 1800–5400) |
| `NTH_CHAOS_MONKEY` | Chaos monkey frequency (default 10 = 1-in-10 chance) |
| `SLEEP_BEFORE_LOCKOUT` | Delay in seconds before applying account lockdown |

## Current State Notes

- The Unifi integration uses `pyunifi` which connects to a local Unifi controller. Use a local admin account (not a cloud/SSO account) as cloud accounts with MFA won't authenticate to the local API.
- `UNIFI_PORT`: use `8443` for standalone Unifi Network Application; use `443` for UDM Pro / UniFi OS consoles.
- The SSH private key (`ssh_private_key`) is committed to the repo and used for all remote operations.
- Firewall status is maintained as internal state in `Unifi` — the controller is not re-queried. On first run, `poll.py` always calls `stop_firewall()` to establish a known state.
