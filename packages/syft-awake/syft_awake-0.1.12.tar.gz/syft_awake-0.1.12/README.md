# Syft Awake 🚀

Fast, secure network awakeness monitoring for SyftBox - ping network members to see who's online and ready for interactive queries.

## Quick Start

### Installation
```bash
pip install syft-awake
```

### Usage
```python
import syft_awake as sa

# Ping a specific user
response = sa.ping_user("friend@example.com", "Are you free for a call?")
if response and response.status == sa.AwakeStatus.AWAKE:
    print(f"{response.responder} is awake: {response.message}")

# Scan the entire network (auto-discovers users with syft-awake)
summary = sa.ping_network()
print(f"Network awakeness: {summary.awakeness_ratio:.1%}")
for user in summary.awake_users:
    print(f"✅ {user} is awake")
```

## What It Does

**Auto-Installation**: Simply importing the library automatically installs the SyftBox app to respond to pings.

**Network Discovery**: Automatically finds other SyftBox users who have syft-awake installed by scanning the local datasites directory.

**Real-time Status**: Get detailed availability info including status (awake/busy/sleeping), workload level, and capabilities.

## API

### Core Functions

**`ping_user(email, message="ping")`** - Ping a specific user  
**`ping_network(user_emails=None)`** - Ping multiple users (auto-discovers if no list provided)

### Status Types
- `AwakeStatus.AWAKE` - Available for interaction  
- `AwakeStatus.BUSY` - Available but occupied
- `AwakeStatus.SLEEPING` - Not available

## Use Cases

**Team Collaboration**
```python
# Check if team is available before starting a meeting
team_emails = ["alice@company.com", "bob@company.com"]  
summary = sa.ping_network(user_emails=team_emails)
if summary.awakeness_ratio > 0.5:
    print("Enough people online for the meeting!")
```

**Distributed Computing**
```python
# Find available compute nodes
summary = sa.ping_network()
light_workload_users = [
    user for user in summary.awake_users 
    if sa.ping_user(user).workload == "light"
]
```

## How It Works

- **Server**: Each user runs a small SyftBox app that responds to awakeness pings
- **Client**: Use this Python library to ping users and scan the network  
- **Security**: Uses SyftBox's authenticated, file-based RPC system
- **Discovery**: Automatically finds users by scanning `/SyftBox/datasites/*/app_data/syft-awake`

## License

Apache 2.0