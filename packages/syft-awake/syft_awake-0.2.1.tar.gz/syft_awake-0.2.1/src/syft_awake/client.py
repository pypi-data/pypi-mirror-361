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

from .models import AwakeRequest, AwakeResponse, AwakeStatus


def ping_user(
    user_email: str,
    timeout: int = 30
) -> Optional[AwakeResponse]:
    """
    Ping a user to check if they're awake.
    
    Args:
        user_email: Email of the user to ping
        timeout: Timeout in seconds to wait for response
    
    Returns:
        AwakeResponse if user responds, None if no response
    
    Example:
        >>> import syft_awake as sa
        >>> response = sa.ping_user("friend@example.com")
        >>> if response:
        ...     print(f"{response.responder} is {response.status}")
    """
    try:
        client = SyftBoxClient.load()
        
        # Create the awakeness ping request
        request = AwakeRequest(
            requester=client.email,
            message="ping",
            priority="normal"
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
    timeout: int = 15
) -> List[AwakeResponse]:
    """
    Ping multiple users. Returns list of successful responses.
    
    Args:
        user_emails: List of emails to ping (if None, discovers from known contacts)
        timeout: Timeout per ping in seconds
    
    Returns:
        List of AwakeResponse objects from users who responded
    
    Example:
        >>> import syft_awake as sa
        >>> responses = sa.ping_network()
        >>> for response in responses:
        ...     print(f"{response.responder} is {response.status}")
    """
    # If no user list provided, try to discover known contacts
    if user_emails is None:
        user_emails = discover_network_members()
    
    responses = []
    
    # Ping users sequentially and collect successful responses
    for user_email in user_emails:
        try:
            response = ping_user(user_email, timeout=timeout)
            if response is not None:
                responses.append(response)
        except Exception:
            continue
    
    return responses


def discover_network_members() -> List[str]:
    """Discover other SyftBox network members to ping."""
    from .discovery import discover_network_members as _discover
    return _discover()


# Define what should be public from this module
__all__ = [
    "ping_user",
    "ping_network",
]