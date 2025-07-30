"""
Debug utilities for troubleshooting syft-awake RPC issues.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

try:
    from syft_core import Client as SyftBoxClient
except ImportError:
    logger.warning("syft_core not available - debug functions limited")
    SyftBoxClient = None


def check_rpc_endpoint(user_email: str) -> Dict[str, Any]:
    """
    Check if a user has syft-awake RPC endpoint available.
    
    Args:
        user_email: Email of the user to check
        
    Returns:
        Dictionary with endpoint information and status
    """
    result = {
        "user_email": user_email,
        "endpoint_exists": False,
        "schema_exists": False,
        "permissions_exists": False,
        "files_found": [],
        "errors": []
    }
    
    try:
        if not SyftBoxClient:
            result["errors"].append("syft_core not available")
            return result
            
        client = SyftBoxClient.load()
        
        # Check if we can access the user's datasite
        # This would need to be adapted based on how SyftBox exposes other users' data
        
        # For now, check local structure as an example
        if user_email == client.email:
            app_data_dir = client.app_data("syft-awake")
            rpc_dir = app_data_dir / "rpc"
            awake_dir = rpc_dir / "awake"
            
            result["endpoint_exists"] = awake_dir.exists()
            result["schema_exists"] = (rpc_dir / "rpc.schema.json").exists()
            result["permissions_exists"] = (rpc_dir / "syftperm.yaml").exists()
            
            if rpc_dir.exists():
                result["files_found"] = [f.name for f in rpc_dir.rglob("*") if f.is_file()]
        else:
            result["errors"].append("Cannot access other users' datasites directly")
            
    except Exception as e:
        result["errors"].append(str(e))
    
    return result


def list_local_rpc_endpoints() -> List[Dict[str, Any]]:
    """
    List all RPC endpoints available on the local SyftBox instance.
    
    Returns:
        List of endpoint information dictionaries
    """
    endpoints = []
    
    try:
        if not SyftBoxClient:
            return []
            
        client = SyftBoxClient.load()
        
        # Check syft-awake endpoints
        app_data_dir = client.app_data("syft-awake")
        rpc_dir = app_data_dir / "rpc"
        
        if rpc_dir.exists():
            for endpoint_dir in rpc_dir.iterdir():
                if endpoint_dir.is_dir() and endpoint_dir.name not in [".", ".."]:
                    endpoints.append({
                        "app": "syft-awake",
                        "endpoint": endpoint_dir.name,
                        "path": str(endpoint_dir),
                        "files": [f.name for f in endpoint_dir.iterdir() if f.is_file()]
                    })
        
        # Could expand to check other apps' RPC endpoints too
        
    except Exception as e:
        logger.error(f"Error listing endpoints: {e}")
    
    return endpoints


def diagnose_ping_failure(user_email: str, error_message: str) -> Dict[str, Any]:
    """
    Analyze a ping failure and provide diagnostic information.
    
    Args:
        user_email: Email of the user that failed to ping
        error_message: The error message received
        
    Returns:
        Dictionary with diagnostic information and suggestions
    """
    diagnosis = {
        "user_email": user_email,
        "error_message": error_message,
        "likely_causes": [],
        "suggestions": [],
        "endpoint_check": None
    }
    
    # Analyze common error patterns
    if "404" in error_message or "not found" in error_message.lower():
        diagnosis["likely_causes"].extend([
            "User doesn't have syft-awake installed",
            "User's syft-awake server is not running", 
            "Endpoint path mismatch",
            "RPC request expired or was cleaned up"
        ])
        diagnosis["suggestions"].extend([
            f"Ask {user_email} to install syft-awake",
            "Check if their SyftBox is running",
            "Verify endpoint path: /api_data/syft-awake/rpc/awake",
            "Try again - request may have expired"
        ])
    elif "timeout" in error_message.lower():
        diagnosis["likely_causes"].extend([
            "User's SyftBox is offline or slow to respond",
            "Network connectivity issues",
            "User's system is under heavy load"
        ])
        diagnosis["suggestions"].extend([
            "Try with a longer timeout",
            "Check network connectivity",
            "Try again later"
        ])
    elif "connection" in error_message.lower():
        diagnosis["likely_causes"].extend([
            "SyftBox sync issues",
            "File system permissions",
            "User's datasite not accessible"
        ])
        diagnosis["suggestions"].extend([
            "Check SyftBox sync status",
            "Verify file permissions",
            "Check if user's datasite is syncing"
        ])
    
    # Check local endpoint status
    diagnosis["endpoint_check"] = check_rpc_endpoint(user_email)
    
    return diagnosis


def debug_rpc_directory(user_email: str) -> Optional[Dict[str, Any]]:
    """
    Debug the RPC directory structure for a user.
    
    Args:
        user_email: Email of the user to debug
        
    Returns:
        Dictionary with directory structure information
    """
    try:
        if not SyftBoxClient:
            return None
            
        client = SyftBoxClient.load()
        
        if user_email != client.email:
            logger.warning("Can only debug local user's RPC directory")
            return None
        
        app_data_dir = client.app_data("syft-awake")
        
        def scan_directory(path: Path) -> Dict[str, Any]:
            """Recursively scan directory structure."""
            result = {"type": "directory", "children": {}}
            
            if not path.exists():
                return {"type": "missing"}
            
            if path.is_file():
                return {
                    "type": "file",
                    "size": path.stat().st_size,
                    "modified": path.stat().st_mtime
                }
            
            for item in path.iterdir():
                result["children"][item.name] = scan_directory(item)
            
            return result
        
        return {
            "user_email": user_email,
            "app_data_dir": str(app_data_dir),
            "structure": scan_directory(app_data_dir)
        }
        
    except Exception as e:
        logger.error(f"Error debugging RPC directory: {e}")
        return None