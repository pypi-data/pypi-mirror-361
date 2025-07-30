#!/usr/bin/env python3
"""
Syft Awake CLI - Command line interface for network awakeness monitoring.

Provides commands for pinging users, scanning the network, and managing
the awakeness monitoring service.
"""

import sys
import argparse
import json
from typing import Optional
from loguru import logger

from .client import ping_user, ping_network, get_awake_users, is_awake
from .discovery import add_known_user, remove_known_user, discover_network_members
from .models import AwakeStatus
from .auto_install import (
    ensure_syftbox_app_installed, 
    reinstall_syftbox_app, 
    is_syftbox_app_installed,
    is_syftbox_running,
    get_syftbox_apps_path
)
from .debug import check_rpc_endpoint, list_local_rpc_endpoints, diagnose_ping_failure


def cmd_ping(args):
    """Ping a specific user to check if they're awake."""
    if not args.user:
        print("Error: User email is required")
        return 1
    
    print(f"📤 Pinging {args.user}...")
    
    response = ping_user(
        user_email=args.user,
        message=args.message or "ping",
        priority=args.priority,
        timeout=args.timeout
    )
    
    if response is None:
        print(f"❌ No response from {args.user}")
        
        # Provide debug suggestions
        print(f"\n💡 Debug suggestions:")
        print(f"   • Run: syft-awake debug {args.user}")
        print(f"   • Check if {args.user} has syft-awake installed")
        print(f"   • Verify their SyftBox is running and syncing")
        
        return 1
    
    status_emoji = {
        AwakeStatus.AWAKE: "✅",
        AwakeStatus.SLEEPING: "😴", 
        AwakeStatus.BUSY: "🔶",
        AwakeStatus.UNKNOWN: "❓"
    }
    
    emoji = status_emoji.get(response.status, "❓")
    print(f"{emoji} {response.responder}: {response.status}")
    print(f"   Message: {response.message}")
    print(f"   Workload: {response.workload}")
    
    if response.response_time_ms:
        print(f"   Response time: {response.response_time_ms:.1f}ms")
    
    if args.json:
        print(json.dumps(response.model_dump(), indent=2, default=str))
    
    return 0


def cmd_scan(args):
    """Scan the network to see who's awake."""
    print("🌐 Scanning network for awake members...")
    
    # Get user list
    if args.users:
        user_emails = args.users.split(',')
    else:
        user_emails = discover_network_members()
        if not user_emails:
            print("No known network members found. Add some with 'syft-awake add-user <email>'")
            return 1
    
    summary = ping_network(
        user_emails=user_emails,
        message=args.message or "network scan",
        timeout=args.timeout
    )
    
    print(f"\n📊 Network Awakeness Summary:")
    print(f"   Total scanned: {summary.total_pinged}")
    print(f"   Awake: {summary.awake_count} ({summary.awakeness_ratio:.1%})")
    print(f"   Responsive: {summary.response_count} ({summary.response_ratio:.1%})")
    print(f"   Scan duration: {summary.scan_duration_ms:.1f}ms")
    
    if summary.awake_users:
        print(f"\n✅ Awake users:")
        for user in summary.awake_users:
            print(f"   • {user}")
    
    if summary.sleeping_users:
        print(f"\n😴 Sleeping users:")
        for user in summary.sleeping_users:
            print(f"   • {user}")
    
    if summary.non_responsive:
        print(f"\n❌ Non-responsive users:")
        for user in summary.non_responsive:
            print(f"   • {user}")
    
    if args.json:
        print(f"\n{json.dumps(summary.model_dump(), indent=2, default=str)}")
    
    return 0


def cmd_check(args):
    """Quick check if specific users are awake."""
    if not args.users:
        print("Error: At least one user email is required")
        return 1
    
    user_emails = args.users.split(',')
    
    for user_email in user_emails:
        user_email = user_email.strip()
        print(f"Checking {user_email}...", end=" ")
        
        if is_awake(user_email, timeout=args.timeout):
            print("✅ AWAKE")
        else:
            print("❌ NOT RESPONDING")
    
    return 0


def cmd_add_user(args):
    """Add a user to the known users list."""
    if not args.user:
        print("Error: User email is required")
        return 1
    
    add_known_user(args.user)
    print(f"✅ Added {args.user} to known users")
    return 0


def cmd_remove_user(args):
    """Remove a user from the known users list."""
    if not args.user:
        print("Error: User email is required")
        return 1
    
    remove_known_user(args.user)
    print(f"➖ Removed {args.user} from known users")
    return 0


def cmd_list_users(args):
    """List all known users."""
    users = discover_network_members()
    
    if not users:
        print("No known users. Add some with 'syft-awake add-user <email>'")
        return 0
    
    print(f"📋 Known network members ({len(users)}):")
    for user in sorted(users):
        print(f"   • {user}")
    
    return 0


def cmd_who_awake(args):
    """Show who is currently awake."""
    print("🔍 Checking who's awake in the network...")
    
    awake_users = get_awake_users(timeout=args.timeout)
    
    if not awake_users:
        print("😴 No users are currently awake (or responding)")
        return 0
    
    print(f"✅ Currently awake ({len(awake_users)}):")
    for user in sorted(awake_users):
        print(f"   • {user}")
    
    return 0


def cmd_install_app(args):
    """Install syft-awake app to SyftBox."""
    print("🚀 Installing syft-awake app to SyftBox...")
    
    if not get_syftbox_apps_path():
        print("❌ SyftBox not found. Please install SyftBox first.")
        return 1
    
    if not is_syftbox_running():
        print("❌ SyftBox is not running. Please start SyftBox first.")
        return 1
    
    if is_syftbox_app_installed():
        print("✅ syft-awake app is already installed")
        return 0
    
    if ensure_syftbox_app_installed(silent=False):
        print("✅ syft-awake app installed successfully")
        print("📝 App will automatically start with SyftBox")
        return 0
    else:
        print("❌ Failed to install syft-awake app")
        return 1


def cmd_reinstall_app(args):
    """Reinstall syft-awake app."""
    print("🔄 Reinstalling syft-awake app...")
    
    if not get_syftbox_apps_path():
        print("❌ SyftBox not found. Please install SyftBox first.")
        return 1
    
    if reinstall_syftbox_app(silent=False):
        print("✅ syft-awake app reinstalled successfully")
        return 0
    else:
        print("❌ Failed to reinstall syft-awake app")
        return 1


def cmd_app_status(args):
    """Check syft-awake app installation status."""
    print("📋 SyftBox App Status:")
    
    apps_path = get_syftbox_apps_path()
    if not apps_path:
        print("   SyftBox: ❌ Not found")
        print("   Install SyftBox to enable awakeness monitoring")
        return 0
    
    print(f"   SyftBox: ✅ Found at {apps_path.parent}")
    
    if is_syftbox_running():
        print("   SyftBox Status: ✅ Running")
    else:
        print("   SyftBox Status: ❌ Not running")
        return 0
    
    if is_syftbox_app_installed():
        print("   syft-awake App: ✅ Installed")
        app_path = apps_path / "syft-awake"
        print(f"   App Location: {app_path}")
        
        # Check if run.sh exists and is executable
        run_sh = app_path / "run.sh"
        if run_sh.exists() and run_sh.stat().st_mode & 0o111:
            print("   run.sh: ✅ Executable")
        else:
            print("   run.sh: ❌ Missing or not executable")
        
    else:
        print("   syft-awake App: ❌ Not installed")
        print("   Run 'syft-awake install' to install the app")
    
    return 0


def cmd_debug(args):
    """Debug RPC endpoint issues."""
    try:
        from syft_core import Client as SyftBoxClient
        client = SyftBoxClient.load()
        user_email = args.user or client.email
    except:
        user_email = args.user or "unknown"
    
    print(f"🔍 Debugging RPC endpoint for {user_email}")
    
    result = check_rpc_endpoint(user_email)
    
    print(f"\n📋 Endpoint Status:")
    print(f"   User: {result['user_email']}")
    print(f"   Endpoint exists: {'✅' if result['endpoint_exists'] else '❌'}")
    print(f"   Schema exists: {'✅' if result['schema_exists'] else '❌'}")
    print(f"   Permissions exist: {'✅' if result['permissions_exists'] else '❌'}")
    
    if result['files_found']:
        print(f"\n📁 Files found:")
        for file in result['files_found']:
            print(f"   • {file}")
    
    if result['errors']:
        print(f"\n❌ Errors:")
        for error in result['errors']:
            print(f"   • {error}")
    
    if args.json:
        print(f"\n{json.dumps(result, indent=2)}")
    
    return 0


def cmd_list_endpoints(args):
    """List local RPC endpoints."""
    print("📡 Local RPC Endpoints:")
    
    endpoints = list_local_rpc_endpoints()
    
    if not endpoints:
        print("   No RPC endpoints found")
        return 0
    
    for endpoint in endpoints:
        print(f"\n   App: {endpoint['app']}")
        print(f"   Endpoint: /{endpoint['endpoint']}")
        print(f"   Path: {endpoint['path']}")
        if endpoint['files']:
            print(f"   Files: {', '.join(endpoint['files'])}")
    
    if args.json:
        print(f"\n{json.dumps(endpoints, indent=2)}")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="syft-awake",
        description="Fast, secure network awakeness monitoring for SyftBox"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="Timeout in seconds (default: 15)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Ping command
    ping_parser = subparsers.add_parser("ping", help="Ping a specific user")
    ping_parser.add_argument("user", help="User email to ping")
    ping_parser.add_argument("--message", "-m", help="Message to send with ping")
    ping_parser.add_argument("--priority", choices=["low", "normal", "high"], 
                           default="normal", help="Priority level")
    ping_parser.set_defaults(func=cmd_ping)
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan network for awake users")
    scan_parser.add_argument("--users", help="Comma-separated list of users to scan")
    scan_parser.add_argument("--message", "-m", help="Message to send with pings")
    scan_parser.set_defaults(func=cmd_scan)
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Quick check if users are awake")
    check_parser.add_argument("users", help="Comma-separated list of users to check")
    check_parser.set_defaults(func=cmd_check)
    
    # User management commands
    add_parser = subparsers.add_parser("add-user", help="Add user to known users list")
    add_parser.add_argument("user", help="User email to add")
    add_parser.set_defaults(func=cmd_add_user)
    
    remove_parser = subparsers.add_parser("remove-user", help="Remove user from known users list")
    remove_parser.add_argument("user", help="User email to remove")
    remove_parser.set_defaults(func=cmd_remove_user)
    
    list_parser = subparsers.add_parser("list-users", help="List all known users")
    list_parser.set_defaults(func=cmd_list_users)
    
    # Quick status commands
    who_parser = subparsers.add_parser("who-awake", help="Show who is currently awake")
    who_parser.set_defaults(func=cmd_who_awake)
    
    # App management commands
    install_parser = subparsers.add_parser("install", help="Install syft-awake app to SyftBox")
    install_parser.set_defaults(func=cmd_install_app)
    
    reinstall_parser = subparsers.add_parser("reinstall", help="Reinstall syft-awake app")
    reinstall_parser.set_defaults(func=cmd_reinstall_app)
    
    status_parser = subparsers.add_parser("app-status", help="Check syft-awake app installation status")
    status_parser.set_defaults(func=cmd_app_status)
    
    # Debug commands
    debug_parser = subparsers.add_parser("debug", help="Debug RPC endpoint issues")
    debug_parser.add_argument("user", nargs="?", help="User email to debug (defaults to self)")
    debug_parser.set_defaults(func=cmd_debug)
    
    endpoints_parser = subparsers.add_parser("list-endpoints", help="List local RPC endpoints")
    endpoints_parser.set_defaults(func=cmd_list_endpoints)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())