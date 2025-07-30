"""
Syft Awake Client - Functions for pinging network members and checking awakeness.

This module provides the main Python library interface for syft-awake.
Use these functions to ping individual users or scan the entire network.
"""

import time
from datetime import datetime, timezone
from typing import List, Dict, Optional, Set
from pathlib import Path
from loguru import logger

# SyftBox integration
try:
    from syft_core import Client as SyftBoxClient
    from syft_rpc import rpc
except ImportError as e:
    logger.warning(f"SyftBox dependencies not available: {e}")
    logger.warning("Some functions will work in demo mode only")
    
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
            logger.info(f"Mock RPC send to {url}")
            
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
        
        # Construct the RPC URL for the target user
        url = f"syft://{user_email}/api_data/syft-awake/rpc/awake"
        
        logger.info(f"📤 Pinging {user_email} with message: '{message}'")
        
        # Send the RPC request
        future = rpc.send(
            url=url,
            body=request.model_dump(),
            expiry="30s",
            cache=False  # Always get fresh awakeness status
        )
        
        # Wait for response
        response = future.wait(timeout=timeout)
        response.raise_for_status()
        
        # Parse the response
        awake_response = response.model(AwakeResponse)
        
        logger.info(f"✅ {user_email} responded: {awake_response.status}")
        return awake_response
        
    except Exception as e:
        logger.warning(f"Failed to ping {user_email}: {e}")
        return None


def is_awake(user_email: str, timeout: int = 10) -> bool:
    """
    Quick check if a user is awake (simplified version of ping_user).
    
    Args:
        user_email: Email of the user to check
        timeout: Timeout in seconds
    
    Returns:
        True if user is awake, False otherwise
    
    Example:
        >>> import syft_awake as sa
        >>> if sa.is_awake("colleague@example.com"):
        ...     print("They're online!")
    """
    response = ping_user(user_email, message="quick_check", timeout=timeout)
    return response is not None and response.status == AwakeStatus.AWAKE


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
    
    logger.info(f"🌐 Scanning network awakeness for {len(user_emails)} users")
    
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
                
        except Exception as e:
            logger.warning(f"Error pinging {user_email}: {e}")
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
    
    logger.info(f"📊 Network scan complete: {summary.awake_count}/{summary.total_pinged} awake")
    logger.info(f"⏱️  Scan took {scan_duration:.1f}ms")
    
    return summary


def get_awake_users(user_emails: Optional[List[str]] = None, timeout: int = 15) -> List[str]:
    """
    Get a list of users who are currently awake.
    
    Args:
        user_emails: List of emails to check (if None, discovers from known contacts)
        timeout: Timeout per ping in seconds
    
    Returns:
        List of email addresses for users who are awake
    
    Example:
        >>> import syft_awake as sa
        >>> awake_users = sa.get_awake_users()
        >>> print(f"Online now: {', '.join(awake_users)}")
    """
    summary = ping_network(user_emails=user_emails, timeout=timeout)
    return summary.awake_users


def discover_network_members() -> List[str]:
    """
    Discover other SyftBox network members to ping.
    
    Returns:
        List of discovered user email addresses
    """
    from .discovery import discover_network_members as _discover
    return _discover()


def ping_with_retry(
    user_email: str,
    message: str = "ping",
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Optional[AwakeResponse]:
    """
    Ping a user with automatic retries for better reliability.
    
    Args:
        user_email: Email of the user to ping
        message: Message to send with ping
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
    
    Returns:
        AwakeResponse if successful, None if all retries failed
    """
    for attempt in range(max_retries + 1):
        try:
            response = ping_user(user_email, message=message)
            if response is not None:
                return response
            
        except Exception as e:
            logger.warning(f"Ping attempt {attempt + 1} failed for {user_email}: {e}")
        
        if attempt < max_retries:
            logger.info(f"Retrying in {retry_delay}s...")
            time.sleep(retry_delay)
    
    logger.error(f"All ping attempts failed for {user_email}")
    return None


# Convenience aliases for shorter import
ping = ping_user
scan = ping_network