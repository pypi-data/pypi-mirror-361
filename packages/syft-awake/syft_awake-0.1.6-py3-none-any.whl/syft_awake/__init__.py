"""
Syft Awake - Network awakeness monitoring for SyftBox

Fast, secure awakeness monitoring that allows SyftBox network members to ping 
each other to check if they're online and ready for interactive queries.
"""

__version__ = "0.1.6"

# Auto-install as SyftBox app if SyftBox is available
try:
    from .auto_install import auto_install as _auto_install, show_startup_banner as _show_startup_banner
    _auto_install()
    
    # Only show banner in interactive environments
    import sys as _sys
    if hasattr(_sys, 'ps1') or _sys.flags.interactive:
        _show_startup_banner()
except Exception:
    # Don't let auto-install errors prevent import
    pass

# Import main functions for easy access
from .client import ping_user, ping_network, is_awake, get_awake_users, has_syft_awake
from .models import AwakeRequest, AwakeResponse, AwakeStatus

__all__ = [
    "ping_user",
    "ping_network", 
    "is_awake",
    "get_awake_users",
    "has_syft_awake",
    "AwakeRequest",
    "AwakeResponse", 
    "AwakeStatus",
]

# Expose auto-install functions for manual use
from .auto_install import ensure_syftbox_app_installed, reinstall_syftbox_app