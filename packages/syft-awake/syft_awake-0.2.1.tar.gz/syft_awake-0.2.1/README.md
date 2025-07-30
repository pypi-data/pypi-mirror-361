# Syft Awake 🚀

See who's online and ready to collaborate in your SyftBox network

## What is it?

Syft Awake helps coordinate live collaboration on [SyftBox](https://www.syftbox.net/) - the open-source platform for privacy-first AI development. Check who's online before starting federated learning experiments, research sessions, or collaborative development.

## Quick Start

```bash
pip install syft-awake
```

```python
import syft_awake as sa

# Ping someone to see if they're online
response = sa.ping_user("colleague@university.edu")
if response:
    print(f"{response.responder} is {response.status}")

# Find everyone who's currently online
responses = sa.ping_network()
online_now = [r.responder for r in responses]
print(f"Online: {', '.join(online_now)}")
```

## Use Cases

**🧪 Research Coordination**
```python
# Check if collaborators are available before starting experiments
research_team = ["alice@university.edu", "bob@lab.org"]
responses = sa.ping_network(research_team)
if len(responses) >= 2:
    print("Enough researchers online - let's start the federated learning!")
```

**🤝 Live Development Sessions**
```python
# See who's available for pair programming or code review
responses = sa.ping_network()
for r in responses:
    if "development" in r.capabilities:
        print(f"{r.responder} is available for development work")
```

**📊 Distributed Computing**
```python
# Find compute nodes with light workload for your job
responses = sa.ping_network()
available_nodes = [r for r in responses if r.workload == "light"]
print(f"Found {len(available_nodes)} available compute nodes")
```

## API

Just two simple functions:

**`ping_user(email, timeout=30)`** → `AwakeResponse` or `None`  
**`ping_network(emails=None, timeout=15)`** → `List[AwakeResponse]`

Auto-installs and auto-discovers network members. Works silently in the background.

## How It Works

- **Automatic**: Simply importing the library installs the SyftBox app
- **Private**: Uses SyftBox's secure, file-based communication  
- **Decentralized**: No central servers - direct peer-to-peer pings
- **Smart Discovery**: Finds other users by scanning your local SyftBox network

Perfect for coordinating real-time collaboration in privacy-preserving AI research and development.

## License

Apache 2.0