"""
Auto-installation functionality for syft-awake SyftBox app.

This module handles automatic installation of the syft-awake app into
SyftBox/apps directory when the library is imported and SyftBox is available.
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import Optional
from loguru import logger

try:
    import requests
    requests_available = True
except ImportError:
    requests_available = False
    requests = None


def get_syftbox_apps_path() -> Optional[Path]:
    """
    Get the SyftBox apps directory path.
    
    Returns:
        Path to ~/SyftBox/apps if it exists, None otherwise
    """
    home = Path.home()
    syftbox_path = home / "SyftBox"
    
    if not syftbox_path.exists():
        return None
        
    apps_path = syftbox_path / "apps"
    return apps_path


def is_syftbox_running() -> bool:
    """
    Check if SyftBox daemon/app is running.
    
    Returns:
        True if SyftBox is running, False otherwise
    """
    try:
        # Try to import syft_core to check if SyftBox is available
        from syft_core import Client as SyftBoxClient
        
        # Try to load the client - this will fail if SyftBox isn't running
        client = SyftBoxClient.load()
        if client and hasattr(client, 'email'):
            return True
            
    except Exception:
        # SyftBox not available or not running
        pass
    
    return False


def is_syftbox_app_installed() -> bool:
    """
    Check if syft-awake app is installed in SyftBox/apps.
    
    Returns:
        True if app is installed, False otherwise
    """
    apps_path = get_syftbox_apps_path()
    if not apps_path:
        return False
        
    app_path = apps_path / "syft-awake"
    return app_path.exists() and app_path.is_dir() and (app_path / "run.sh").exists()


def clone_syftbox_app() -> bool:
    """
    Clone syft-awake repository into SyftBox/apps directory.
    
    Returns:
        True if successful, False otherwise
    """
    apps_path = get_syftbox_apps_path()
    if not apps_path:
        logger.warning("SyftBox directory not found")
        return False
    
    # Ensure apps directory exists
    apps_path.mkdir(parents=True, exist_ok=True)
    
    # Repository URL - for now, we'll use a fallback approach
    # TODO: Update this to the actual public repo URL when available
    repo_url = "https://github.com/OpenMined/syft-awake.git"
    target_path = apps_path / "syft-awake"
    
    try:
        # Check if git is available
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        
        # Remove existing directory if it exists
        if target_path.exists():
            import shutil
            shutil.rmtree(target_path)
        
        # Clone the repository
        logger.info(f"Cloning syft-awake to {target_path}")
        result = subprocess.run(
            ["git", "clone", repo_url, str(target_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Make run.sh executable
            run_sh = target_path / "run.sh"
            if run_sh.exists():
                run_sh.chmod(0o755)
            logger.info("✅ syft-awake app installed successfully")
            return True
        else:
            logger.error(f"Git clone failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Git clone timed out")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e}")
        return False
    except FileNotFoundError:
        logger.error("Git not found - please install git")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during clone: {e}")
        return False


def copy_bundled_app_to_syftbox() -> bool:
    """
    Copy the bundled syftbox_app to SyftBox/apps directory.
    This uses the app bundle included with the Python package.
    
    Returns:
        True if successful, False otherwise
    """
    apps_path = get_syftbox_apps_path()
    if not apps_path:
        return False
    
    # Find the bundled app directory
    current_file = Path(__file__).resolve()
    bundled_app_path = current_file.parent / "syftbox_app"
    
    # Check if bundled app exists
    if not bundled_app_path.exists() or not (bundled_app_path / "run.sh").exists():
        logger.debug("Bundled app not found")
        return False
    
    target_path = apps_path / "syft-awake"
    
    try:
        import shutil
        
        # Remove existing directory if it exists
        if target_path.exists():
            shutil.rmtree(target_path)
        
        # Copy the bundled app
        shutil.copytree(bundled_app_path, target_path)
        
        # Make run.sh executable
        run_sh = target_path / "run.sh"
        if run_sh.exists():
            run_sh.chmod(0o755)
        
        logger.info(f"✅ Installed bundled syft-awake app to {target_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to copy bundled app: {e}")
        return False


def copy_local_app_to_syftbox() -> bool:
    """
    Copy the local syft-awake app to SyftBox/apps directory.
    This is used when the library is being developed locally.
    
    Returns:
        True if successful, False otherwise
    """
    apps_path = get_syftbox_apps_path()
    if not apps_path:
        return False
    
    # Find the local app directory (where this file is located)
    current_file = Path(__file__).resolve()
    # Go up from src/syft_awake/auto_install.py to the root
    local_app_path = current_file.parent.parent.parent
    
    # Check if this looks like a syft-awake app directory
    if not (local_app_path / "run.sh").exists():
        return False
    
    target_path = apps_path / "syft-awake"
    
    try:
        import shutil
        
        # Remove existing directory if it exists
        if target_path.exists():
            shutil.rmtree(target_path)
        
        # Copy the entire directory
        shutil.copytree(local_app_path, target_path)
        
        # Make run.sh executable
        run_sh = target_path / "run.sh"
        if run_sh.exists():
            run_sh.chmod(0o755)
        
        logger.info(f"✅ Copied local syft-awake app to {target_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to copy local app: {e}")
        return False


def ensure_syftbox_app_installed(silent: bool = True) -> bool:
    """
    Ensure syft-awake app is installed in SyftBox but don't auto-start server.
    
    Args:
        silent: If True, suppress most output messages
        
    Returns:
        True if app is installed or installation succeeded, False otherwise
    """
    apps_path = get_syftbox_apps_path()
    if not apps_path:
        # SyftBox not found - normal for non-SyftBox users
        if not silent:
            logger.info("SyftBox not found - running in standalone mode")
        return False
    
    if not is_syftbox_running():
        if not silent:
            logger.warning("SyftBox is not running. Please start SyftBox first.")
        return False
    
    if not is_syftbox_app_installed():
        if not silent:
            logger.info("SyftBox detected but syft-awake app not found. Attempting auto-installation...")
        
        # Try installation methods in order of preference:
        
        # 1. Try copying local app (for development)
        if copy_local_app_to_syftbox():
            if not silent:
                logger.info("✅ Local development app installed successfully")
            return True
        
        # 2. Try copying bundled app (for PyPI releases)
        if copy_bundled_app_to_syftbox():
            if not silent:
                logger.info("✅ Bundled app installed successfully")
                logger.info("📝 App will automatically start with SyftBox")
            return True
        
        # 3. Fallback to git clone (if repo is available)
        if clone_syftbox_app():
            if not silent:
                logger.info("✅ App installed successfully from git")
                logger.info("📝 App will automatically start with SyftBox")
            return True
        else:
            if not silent:
                logger.warning("❌ Failed to install syft-awake app automatically")
                logger.info("💡 Manual installation options:")
                logger.info("   1. Run: syft-awake install")
                logger.info("   2. Copy app manually to ~/SyftBox/apps/syft-awake")
                logger.info("   3. Clone repo: git clone <repo-url> ~/SyftBox/apps/syft-awake")
            return False
    
    if not silent:
        logger.info("✅ syft-awake app already installed")
    return True


def check_app_health() -> bool:
    """
    Check if the syft-awake app is running and healthy.
    
    Returns:
        True if app is responding to health checks, False otherwise
    """
    if not requests_available:
        return False
    
    try:
        # Try to ping the awakeness endpoint of the local user
        from syft_core import Client as SyftBoxClient
        client = SyftBoxClient.load()
        
        # Try a quick self-ping to see if our server is running
        from .client import ping_user
        response = ping_user(client.email, message="health_check", timeout=5)
        return response is not None
        
    except Exception:
        return False


def auto_install() -> bool:
    """
    Main auto-installation function called during library import.
    
    This function is designed to be called automatically when the
    syft_awake library is imported. It will:
    
    1. Check if SyftBox is available and running
    2. Install the syft-awake app if needed
    3. Gracefully handle all errors to not break imports
    
    Returns:
        True if installation succeeded or wasn't needed, False if failed
    """
    try:
        # Only proceed if SyftBox is available
        if not get_syftbox_apps_path():
            return False
        
        if not is_syftbox_running():
            return False
        
        # Try to install the app
        return ensure_syftbox_app_installed(silent=True)
        
    except Exception as e:
        # Never let auto-install errors break library imports
        logger.debug(f"Auto-install failed: {e}")
        return False


def show_startup_banner():
    """
    Show a friendly startup banner when syft-awake is imported in interactive mode.
    """
    try:
        if is_syftbox_app_installed():
            logger.info("🚀 syft-awake: Network awakeness monitoring ready!")
            logger.info("   Use 'import syft_awake as sa' to ping network members")
        else:
            logger.info("📦 syft-awake library loaded")
            logger.info("   Install SyftBox to enable network awakeness monitoring")
    except Exception:
        # Don't let banner errors break anything
        pass


def reinstall_syftbox_app(silent: bool = False) -> bool:
    """
    Force reinstall the syft-awake app.
    
    Args:
        silent: If True, suppress output messages
        
    Returns:
        True if reinstall succeeded, False otherwise
    """
    apps_path = get_syftbox_apps_path()
    if not apps_path:
        if not silent:
            logger.error("SyftBox not found")
        return False
    
    target_path = apps_path / "syft-awake"
    
    try:
        # Remove existing installation
        if target_path.exists():
            import shutil
            shutil.rmtree(target_path)
            if not silent:
                logger.info("Removed existing installation")
        
        # Try local copy first, then git clone
        if copy_local_app_to_syftbox() or clone_syftbox_app():
            if not silent:
                logger.info("✅ syft-awake reinstalled successfully")
            return True
        else:
            if not silent:
                logger.error("❌ Reinstallation failed")
            return False
            
    except Exception as e:
        if not silent:
            logger.error(f"Reinstallation failed: {e}")
        return False