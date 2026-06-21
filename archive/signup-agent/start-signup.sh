#!/bin/bash

# Signup Agent Quick Start Script
# Usage: ./start-signup.sh [directory-name]

cd "$(dirname "$0")"

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

if [ -z "$1" ]; then
    echo "Usage: ./start-signup.sh <directory-name>"
    echo ""
    echo "Available directories:"
    node cli.js --list
    echo ""
    echo "Or run all: ./start-signup.sh --all"
    exit 1
fi

node cli.js --directory "$1"
