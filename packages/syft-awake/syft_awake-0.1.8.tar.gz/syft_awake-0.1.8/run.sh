#!/bin/bash
set -e

# SyftBox app entry point for syft-awake
echo "🚀 Syft Awake - Starting awakeness monitoring service..."

# Disable interactive prompts for non-interactive environments
export ZSH_DISABLE_COMPFIX=true
export NONINTERACTIVE=1

# Detect if we're running inside SyftBox
if [ -n "$SYFTBOX_ASSIGNED_PORT" ]; then
    PORT=$SYFTBOX_ASSIGNED_PORT
    echo -e "Running as SyftBox app on port $PORT"
else
    PORT=${SYFT_AWAKE_PORT:-8080}
    echo -e "Running standalone on port $PORT"
fi

# Setup Python environment with uv (per CLAUDE.md requirements)
echo "📦 Setting up virtual environment with uv..."

# Create virtual environment (remove old one if exists)
rm -rf .venv

# Use Python 3.12 (recommended)
uv venv --python 3.12

# Set the virtual environment path
export VIRTUAL_ENV="$(pwd)/.venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Export port for the application
export SYFT_AWAKE_PORT=$PORT

# Run the main awakeness monitoring service
echo "🔄 Starting awakeness monitoring service..."
echo "⚡ Ready to respond to awakeness pings from network members"
uv run python -m syft_awake.app