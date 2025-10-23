#!/bin/bash

# Setup script for Beads issue tracker
# This script adds the Go bin directory to PATH and provides convenient aliases

echo "Setting up Beads for Laurelin Chat Backend..."

# Add Go bin to PATH for this session
export PATH="$PATH:/Users/Joe/go/bin"

# Check if bd is accessible
if command -v bd &> /dev/null; then
    echo "✓ Beads (bd) is accessible"
    bd version
else
    echo "✗ Beads (bd) not found in PATH"
    echo "Make sure Go is installed and bd is in /Users/Joe/go/bin/"
    exit 1
fi

# Show current project status
echo ""
echo "Current project issues:"
bd list

echo ""
echo "Ready work (no blockers):"
bd ready

echo ""
echo "To use Beads in future sessions, add this to your shell profile:"
echo "export PATH=\"\$PATH:/Users/Joe/go/bin\""
echo ""
echo "Or run this script: source ./setup-beads.sh"
