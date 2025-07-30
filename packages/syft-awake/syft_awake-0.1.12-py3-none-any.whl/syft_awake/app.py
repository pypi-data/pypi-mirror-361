#!/usr/bin/env python3
"""
Syft Awake - Main awakeness monitoring server

This server responds to awakeness pings from other SyftBox network members,
indicating whether the user is awake and available for interactive queries.
"""

import time
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path
from loguru import logger
from typing import Optional

# SyftBox integration
try:
    from syft_core import Client as SyftBoxClient
    from syft_event import SyftEvents
    from syft_event.types import Request
except ImportError as e:
    logger.warning(f"SyftBox dependencies not available: {e}")
    logger.warning("Running in demo mode")
    
    # Mock classes for development/testing
    class MockSyftBoxClient:
        def __init__(self):
            self.email = "demo@example.com"
        
        def app_data(self, app_name):
            import tempfile
            return Path(tempfile.gettempdir()) / f"syftbox_demo_{app_name}"
        
        @classmethod
        def load(cls):
            return cls()
    
    class MockSyftEvents:
        def __init__(self, app_name):
            self.app_name = app_name
            self.client = MockSyftBoxClient()
            
        def on_request(self, endpoint):
            def decorator(func):
                logger.info(f"Mock: Would register {endpoint} handler")
                return func
            return decorator
            
        def run_forever(self):
            logger.info("Mock: Would run server forever")
            import time
            while True:
                time.sleep(60)
    
    SyftBoxClient = MockSyftBoxClient
    SyftEvents = MockSyftEvents
    Request = object

from .models import AwakeRequest, AwakeResponse, AwakeStatus


class AwakeServer:
    """Awakeness monitoring server that responds to network pings."""
    
    def __init__(self):
        """Initialize the awakeness server."""
        try:
            # Initialize SyftBox client
            self.syftbox_client = SyftBoxClient.load()
            self.email = self.syftbox_client.email
            
            # Initialize SyftEvents for handling RPC requests
            self.events = SyftEvents("syft-awake")
            
            # Get app-specific data directory
            self.app_data_dir = self.syftbox_client.app_data("syft-awake")
            self.app_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Create permissions file in api_data directory for RPC syncing
            self.setup_api_permissions()
            
            # User's awakeness configuration
            self.config_file = self.app_data_dir / "awake_config.json"
            self.load_config()
            
            logger.info(f"✅ Initialized Syft Awake server for {self.email}")
            logger.info(f"📁 App data directory: {self.app_data_dir}")
            
        except Exception as e:
            logger.warning(f"Could not initialize SyftBox client: {e}")
            # Set up in demo mode
            self.syftbox_client = SyftBoxClient()
            self.email = self.syftbox_client.email
            self.app_data_dir = Path("./demo_data")
            self.app_data_dir.mkdir(exist_ok=True)
            self.events = SyftEvents("syft-awake")
            self.config_file = self.app_data_dir / "awake_config.json"
            self.load_config()
            
        # Register the awakeness endpoint
        self.register_handlers()
    
    def load_config(self):
        """Load user's awakeness configuration."""
        default_config = {
            "auto_respond": True,
            "default_status": "awake",
            "default_message": "I'm awake and ready to help!",
            "workload": "light",
            "capabilities": {
                "queries": True,
                "collaboration": True,
                "data_processing": True
            }
        }
        
        if self.config_file.exists():
            import json
            try:
                with open(self.config_file, 'r') as f:
                    self.config = {**default_config, **json.load(f)}
            except Exception as e:
                logger.warning(f"Error loading config: {e}, using defaults")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save user's awakeness configuration."""
        import json
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def setup_api_permissions(self):
        """Set up permissions file in api_data directory for RPC syncing."""
        try:
            # Get the api_data directory path
            home = Path.home()
            api_data_dir = home / "SyftBox" / "datasites" / self.email / "api_data" / "syft-awake"
            api_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Create syft.pub.yaml in api_data directory
            permissions_file = api_data_dir / "syft.pub.yaml"
            
            if not permissions_file.exists():
                permissions_content = """rules:
- pattern: 'rpc/rpc.schema.json'
  access:
    read:
    - '*'
- pattern: 'rpc/**/*.request'
  access:
    read:
    - '*'
    write:
    - '*'
    admin:
    - '*'
- pattern: 'rpc/**/*.response'
  access:
    read:
    - '*'
    write:
    - '*'
    admin:
    - '*'
"""
                permissions_file.write_text(permissions_content)
                logger.info(f"✅ Created permissions file at {permissions_file}")
            else:
                logger.debug(f"Permissions file already exists at {permissions_file}")
                
        except Exception as e:
            logger.error(f"Failed to set up API permissions: {e}")
    
    def register_handlers(self):
        """Register RPC endpoint handlers."""
        
        @self.events.on_request("/awake")
        def handle_awake_ping(request: AwakeRequest, ctx: Request) -> AwakeResponse:
            """Handle incoming awakeness ping requests."""
            start_time = time.time()
            
            logger.info(f"📨 Received awakeness ping from {request.requester}")
            logger.info(f"   Message: {request.message}")
            logger.info(f"   Priority: {request.priority}")
            
            # Generate response based on current status and config
            response = self.generate_awake_response(request)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            response.response_time_ms = response_time
            
            logger.info(f"✅ Responding with status: {response.status}")
            logger.info(f"   Response time: {response_time:.1f}ms")
            
            return response
    
    def generate_awake_response(self, request: AwakeRequest) -> AwakeResponse:
        """Generate an appropriate awakeness response."""
        
        # Determine current status (could be enhanced with more logic)
        current_status = AwakeStatus(self.config.get("default_status", "awake"))
        
        # Create personalized message
        message = self.config.get("default_message", "I'm awake!")
        if request.priority == "high":
            message = f"🚨 {message} (High priority noted)"
        elif request.message and request.message != "ping":
            message = f"{message} Re: {request.message}"
        
        # Build response
        response = AwakeResponse(
            responder=self.email,
            status=current_status,
            message=message,
            workload=self.config.get("workload", "light"),
            capabilities=self.config.get("capabilities", {})
        )
        
        return response
    
    def update_status(self, status: AwakeStatus, message: Optional[str] = None):
        """Update the user's awakeness status."""
        self.config["default_status"] = status.value
        if message:
            self.config["default_message"] = message
        self.save_config()
        logger.info(f"🔄 Status updated to: {status.value}")
    
    def update_workload(self, workload: str):
        """Update the user's current workload level."""
        self.config["workload"] = workload
        self.save_config()
        logger.info(f"⚡ Workload updated to: {workload}")
    
    def run(self):
        """Start the awakeness monitoring server."""
        logger.info("🚀 Starting Syft Awake server...")
        logger.info(f"📡 Listening for awakeness pings at: syft://{self.email}/api_data/syft-awake/rpc/awake")
        logger.info("⚡ Ready to respond to network awakeness checks")
        
        # Set up graceful shutdown
        def signal_handler(signum, frame):
            logger.info("👋 Shutting down Syft Awake server gracefully...")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Run the SyftEvents server
            self.events.run_forever()
        except KeyboardInterrupt:
            logger.info("👋 Server stopped by user")
        except Exception as e:
            logger.error(f"❌ Server error: {e}")
            raise


def main():
    """Main entry point for the awakeness server."""
    try:
        server = AwakeServer()
        server.run()
    except Exception as e:
        logger.error(f"Failed to start Syft Awake server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()