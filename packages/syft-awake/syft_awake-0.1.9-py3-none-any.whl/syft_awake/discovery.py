"""
Network discovery functionality for finding SyftBox network members.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Set, Dict, Optional
from loguru import logger

try:
    from syft_core import Client as SyftBoxClient
except ImportError:
    logger.warning("syft_core not available - using mock discovery")
    
    class MockSyftBoxClient:
        def __init__(self):
            self.email = "demo@example.com"
        
        @classmethod
        def load(cls):
            return cls()
    
    SyftBoxClient = MockSyftBoxClient


class NetworkDiscovery:
    """Discovers other SyftBox network members for awakeness monitoring."""
    
    def __init__(self):
        self.client = SyftBoxClient.load()
        self.known_users: Set[str] = set()
        self.user_cache_file = self._get_cache_file()
        self.load_known_users()
    
    def _get_cache_file(self) -> Path:
        """Get the path to the user cache file."""
        try:
            # Try to use SyftBox app data directory
            app_data = self.client.app_data("syft-awake")
            app_data.mkdir(parents=True, exist_ok=True)
            return app_data / "known_users.json"
        except:
            # Fallback to local directory
            return Path("known_users.json")
    
    def load_known_users(self):
        """Load previously discovered users from cache."""
        if self.user_cache_file.exists():
            try:
                with open(self.user_cache_file, 'r') as f:
                    data = json.load(f)
                    self.known_users = set(data.get("users", []))
                logger.info(f"📚 Loaded {len(self.known_users)} known users from cache")
            except Exception as e:
                logger.warning(f"Failed to load user cache: {e}")
                self.known_users = set()
    
    def save_known_users(self):
        """Save discovered users to cache."""
        try:
            data = {
                "users": list(self.known_users),
                "last_updated": str(datetime.now(timezone.utc))
            }
            with open(self.user_cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"💾 Saved {len(self.known_users)} users to cache")
        except Exception as e:
            logger.warning(f"Failed to save user cache: {e}")
    
    def add_user(self, user_email: str):
        """Add a user to the known users list."""
        if user_email and user_email != self.client.email:
            self.known_users.add(user_email)
            self.save_known_users()
            logger.info(f"➕ Added {user_email} to known users")
    
    def remove_user(self, user_email: str):
        """Remove a user from the known users list."""
        if user_email in self.known_users:
            self.known_users.remove(user_email)
            self.save_known_users()
            logger.info(f"➖ Removed {user_email} from known users")
    
    def discover_from_syftbox_network(self) -> List[str]:
        """
        Discover users from SyftBox network structures.
        
        Scans the SyftBox datasites directory to find users who have 
        syft-awake installed by looking for app_data/syft-awake directories.
        """
        discovered = []
        
        try:
            logger.info("🔍 Scanning SyftBox datasites for syft-awake installations...")
            
            # Get the SyftBox datasites directory path
            home_path = Path.home()
            datasites_path = home_path / "SyftBox" / "datasites"
            
            if not datasites_path.exists():
                logger.debug(f"SyftBox datasites directory not found: {datasites_path}")
                return discovered
            
            # Scan each datasite for syft-awake app installation
            for datasite_dir in datasites_path.iterdir():
                if not datasite_dir.is_dir():
                    continue
                
                # Check if this user has syft-awake installed
                syft_awake_path = datasite_dir / "app_data" / "syft-awake"
                if syft_awake_path.exists() and syft_awake_path.is_dir():
                    user_email = datasite_dir.name
                    
                    # Skip ourselves
                    if user_email != self.client.email:
                        discovered.append(user_email)
                        logger.debug(f"Found syft-awake installation for: {user_email}")
            
            logger.info(f"📡 Discovered {len(discovered)} users with syft-awake installed")
            
        except Exception as e:
            logger.warning(f"SyftBox network discovery failed: {e}")
        
        # Add any newly discovered users
        for user in discovered:
            self.add_user(user)
        
        return discovered
    
    def discover_from_rpc_logs(self) -> List[str]:
        """
        Discover users from recent RPC interaction logs.
        
        Examines syft-rpc logs or request/response files to find
        users who have recently been active in the network.
        """
        discovered = []
        
        try:
            # TODO: Implement RPC log scanning
            # Look for recent .request and .response files
            # Parse sender/receiver information
            
            logger.info("📝 Scanning RPC logs for active users...")
            
        except Exception as e:
            logger.warning(f"RPC log discovery failed: {e}")
        
        for user in discovered:
            self.add_user(user)
        
        return discovered
    
    def discover_from_shared_directories(self) -> List[str]:
        """
        Discover users from shared directories or collaborative spaces.
        
        Looks at syftperm.yaml files and shared data directories
        to find users who have been granted access or have contributed.
        """
        discovered = []
        
        try:
            # TODO: Implement shared directory scanning
            # Look for syftperm.yaml files
            # Parse user permissions and access lists
            
            logger.info("📂 Scanning shared directories for users...")
            
        except Exception as e:
            logger.warning(f"Shared directory discovery failed: {e}")
        
        for user in discovered:
            self.add_user(user)
        
        return discovered
    
    def get_all_known_users(self) -> List[str]:
        """Get all known users (cached + newly discovered)."""
        # Start with cached users
        all_users = set(self.known_users)
        
        # Add newly discovered users from various sources
        try:
            all_users.update(self.discover_from_syftbox_network())
            all_users.update(self.discover_from_rpc_logs())
            all_users.update(self.discover_from_shared_directories())
        except Exception as e:
            logger.warning(f"Discovery process failed: {e}")
        
        # Remove self from the list
        all_users.discard(self.client.email)
        
        result = list(all_users)
        logger.info(f"🌐 Total known network members: {len(result)}")
        
        return result
    
    def suggest_users_to_add(self) -> List[str]:
        """Suggest users that might be worth adding to the network."""
        suggestions = []
        
        # This could implement heuristics like:
        # - Users who frequently appear in RPC logs
        # - Users with public awakeness endpoints
        # - Users in collaborative projects
        
        return suggestions


# Global discovery instance
_discovery = None

def get_discovery() -> NetworkDiscovery:
    """Get the global network discovery instance."""
    global _discovery
    if _discovery is None:
        _discovery = NetworkDiscovery()
    return _discovery


def discover_network_members() -> List[str]:
    """Convenience function to discover network members."""
    return get_discovery().get_all_known_users()


def add_known_user(user_email: str):
    """Add a user to the known users list."""
    get_discovery().add_user(user_email)


def remove_known_user(user_email: str):
    """Remove a user from the known users list.""" 
    get_discovery().remove_user(user_email)