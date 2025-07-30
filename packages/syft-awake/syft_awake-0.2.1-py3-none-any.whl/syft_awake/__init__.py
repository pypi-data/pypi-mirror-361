"""
Syft Awake - Network awakeness monitoring for SyftBox

Fast, secure awakeness monitoring that allows SyftBox network members to ping 
each other to check if they're online and ready for interactive queries.
"""

__version__ = "0.2.1"

# Auto-install as SyftBox app if SyftBox is available
try:
    import importlib
    _auto_mod = importlib.import_module('.auto_install', package=__name__)
    _auto_mod.auto_install()
    del importlib, _auto_mod
except Exception:
    pass

# Import core functions only - use importlib to avoid namespace pollution
import importlib as _importlib
_client_mod = _importlib.import_module('.client', package=__name__)

ping_user = _client_mod.ping_user
ping_network = _client_mod.ping_network

del _importlib, _client_mod

__all__ = [
    "ping_user",
    "ping_network",
]

# Clean up namespace completely
import sys as _sys
_this_module = _sys.modules[__name__]
_all_names = list(globals().keys())
for _name in _all_names:
    if _name not in __all__ and not _name.startswith('_') and _name not in ['__doc__', '__file__', '__name__', '__package__', '__path__', '__spec__', '__version__']:
        try:
            delattr(_this_module, _name)
        except (AttributeError, ValueError):
            pass
del _sys, _this_module, _all_names, _name