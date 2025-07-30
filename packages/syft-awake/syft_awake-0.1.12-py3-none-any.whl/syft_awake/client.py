"""
Syft Awake Client - Functions for pinging network members and checking awakeness.

This module provides the main Python library interface for syft-awake.
Use these functions to ping individual users or scan the entire network.
"""

import time
from datetime import datetime, timezone
from typing import List, Dict, Optional, Set
from pathlib import Path

# SyftBox integration
try:
    from syft_core import Client as SyftBoxClient
    from syft_rpc import rpc
except ImportError:
    
    # Mock classes for development/testing
    class MockSyftBoxClient:
        def __init__(self):
            self.email = "demo@example.com"
        
        @classmethod
        def load(cls):
            return cls()
    
    class MockRPC:
        @staticmethod
        def send(url, body, expiry="30s", cache=False):
            class MockFuture:
                def wait(self, timeout=30):
                    # Simulate some response delay
                    time.sleep(0.1)
                    
                    class MockResponse:
                        def raise_for_status(self):
                            pass
                        
                        def model(self, model_class):
                            from .models import AwakeResponse, AwakeStatus
                            return AwakeResponse(
                                responder="mock@example.com",
                                status=AwakeStatus.AWAKE,
                                message="Mock response - I'm awake!",
                                workload="light"
                            )
                    
                    return MockResponse()
            
            return MockFuture()
    
    SyftBoxClient = MockSyftBoxClient
    rpc = MockRPC()

from .models import AwakeRequest, AwakeResponse, AwakeStatus, NetworkAwakenessSummary


def ping_user(
    user_email: str, 
    message: str = "ping",
    priority: str = "normal",
    timeout: int = 30
) -> Optional[AwakeResponse]:
    """
    Ping a specific user to check if they're awake.
    
    Args:
        user_email: Email of the user to ping
        message: Optional message to send with the ping
        priority: Priority level (low, normal, high)
        timeout: Timeout in seconds to wait for response
    
    Returns:
        AwakeResponse if user responds, None if no response
    
    Example:
        >>> import syft_awake as sa
        >>> response = sa.ping_user("friend@example.com", "Are you free for a quick call?")
        >>> if response and response.status == sa.AwakeStatus.AWAKE:
        ...     print(f"{response.responder} is awake: {response.message}")
    """
    try:
        client = SyftBoxClient.load()
        
        # Create the awakeness ping request
        request = AwakeRequest(
            requester=client.email,
            message=message,
            priority=priority
        )
        
        # Construct the RPC URL for the target user using rpc.make_url()
        url = rpc.make_url(datasite=user_email, app_name="syft-awake", endpoint="awake")
        
        future = rpc.send(
            url=url,
            body=request,
            expiry="30s",
            cache=False
        )
        
        response = future.wait(timeout=timeout)
        response.raise_for_status()
        
        # Parse the response
        awake_response = response.model(AwakeResponse)
        return awake_response
        
    except Exception:
        return None


def ping_network(
    user_emails: Optional[List[str]] = None,
    message: str = "network scan",
    timeout: int = 15,
    max_concurrent: int = 10
) -> NetworkAwakenessSummary:
    """
    Ping multiple users concurrently to check network awakeness.
    
    Args:
        user_emails: List of emails to ping (if None, discovers from known contacts)
        message: Message to send with pings
        timeout: Timeout per ping in seconds
        max_concurrent: Maximum concurrent pings
    
    Returns:
        NetworkAwakenessSummary with results
    
    Example:
        >>> import syft_awake as sa
        >>> summary = sa.ping_network()
        >>> print(f"Network awakeness: {summary.awakeness_ratio:.1%}")
        >>> for user in summary.awake_users:
        ...     print(f"✅ {user} is awake")
    """
    start_time = time.time()
    
    # If no user list provided, try to discover known contacts
    if user_emails is None:
        user_emails = discover_network_members()
    
    awake_users = []
    sleeping_users = []
    non_responsive = []
    
    # TODO: Implement concurrent pinging for better performance
    # For now, ping sequentially to keep it simple
    for user_email in user_emails:
        try:
            response = ping_user(user_email, message=message, timeout=timeout)
            
            if response is None:
                non_responsive.append(user_email)
            elif response.status == AwakeStatus.AWAKE:
                awake_users.append(user_email)
            else:
                sleeping_users.append(user_email)
                
        except Exception:
            non_responsive.append(user_email)
    
    scan_duration = (time.time() - start_time) * 1000
    
    summary = NetworkAwakenessSummary(
        total_pinged=len(user_emails),
        awake_count=len(awake_users),
        response_count=len(awake_users) + len(sleeping_users),
        awake_users=awake_users,
        sleeping_users=sleeping_users,
        non_responsive=non_responsive,
        scan_duration_ms=scan_duration
    )
    
    return summary


def discover_network_members() -> List[str]:
    """Discover other SyftBox network members to ping."""
    from .discovery import discover_network_members as _discover
    return _discover()


# Define what should be public from this module
__all__ = [
    "ping_user",
    "ping_network",
]