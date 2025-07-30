# Syft Awake SyftBox App

This is the SyftBox app version of syft-awake that gets automatically installed to `~/SyftBox/apps/syft-awake/`.

## What it does

- Responds to awakeness pings from other network members
- Provides your awakeness status (awake/sleeping/busy)
- Enables real-time collaboration and presence monitoring

## How it works

This app:
1. Installs the syft-awake Python package from PyPI
2. Runs the awakeness monitoring server
3. Listens for RPC requests at `syft://{your-email}/api_data/syft-awake/rpc/awake`

## Configuration

The app automatically loads your configuration from:
`~/.syftbox/api_data/syft-awake/awake_config.json`

You can customize your:
- Default awakeness status
- Response messages
- Workload indicators
- Capabilities

## Manual Installation

If auto-installation failed, you can manually install:

```bash
# Copy this directory to SyftBox apps
cp -r syftbox_app ~/SyftBox/apps/syft-awake

# Or use the CLI
syft-awake install
```