#!/bin/bash
# MFM Corporation Dashboard Startup Script
# Fixes Render's src/ directory issue by finding the correct path

# Find the project root (where enhanced_dashboard_server.py lives)
PROJECT_ROOT=""

# Check common Render paths
if [ -f "/opt/render/project/enhanced_dashboard_server.py" ]; then
    PROJECT_ROOT="/opt/render/project"
elif [ -f "../enhanced_dashboard_server.py" ]; then
    PROJECT_ROOT=".."
elif [ -f "./enhanced_dashboard_server.py" ]; then
    PROJECT_ROOT="."
fi

# If still not found, search recursively
if [ -z "$PROJECT_ROOT" ]; then
    FOUND=$(find /opt/render -name "enhanced_dashboard_server.py" -not -path "*/\.*" | head -1)
    if [ -n "$FOUND" ]; then
        PROJECT_ROOT=$(dirname "$FOUND")
    fi
fi

# Change to project root and start server
cd "$PROJECT_ROOT"
echo "Starting MFM Dashboard from: $(pwd)"
python enhanced_dashboard_server.py
