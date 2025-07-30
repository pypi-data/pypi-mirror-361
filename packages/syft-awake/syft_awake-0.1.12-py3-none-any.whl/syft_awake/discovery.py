"""
Network discovery functionality for finding SyftBox network members.
"""

from pathlib import Path
from typing import List

try:
    from syft_core import Client as SyftBoxClient
except ImportError:
    class MockSyftBoxClient:
        def __init__(self):
            self.email = "demo@example.com"
        
        @classmethod
        def load(cls):
            return cls()
    
    SyftBoxClient = MockSyftBoxClient


def discover_network_members() -> List[str]:
    """Discover SyftBox users who have syft-awake installed."""
    try:
        client = SyftBoxClient.load()
        
        # Get the SyftBox datasites directory path
        home_path = Path.home()
        datasites_path = home_path / "SyftBox" / "datasites"
        
        if not datasites_path.exists():
            return []
        
        discovered = []
        
        # Scan each datasite for syft-awake app installation
        for datasite_dir in datasites_path.iterdir():
            if not datasite_dir.is_dir():
                continue
            
            # Check if this user has syft-awake installed
            syft_awake_path = datasite_dir / "app_data" / "syft-awake"
            if syft_awake_path.exists() and syft_awake_path.is_dir():
                user_email = datasite_dir.name
                
                # Skip ourselves
                if user_email != client.email:
                    discovered.append(user_email)
        
        return discovered
        
    except Exception:
        return []