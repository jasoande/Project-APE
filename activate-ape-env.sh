#!/bin/bash
# project ape Account Intelligence - Virtual Environment Activation Script
# Source this script to activate the project ape Account Intelligence virtual environment

VENV_DIR="$HOME/.project-ape-venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at: $VENV_DIR"
    echo "Run ./setup-environment.sh first"
    return 1 2>/dev/null || exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

if [[ "$VIRTUAL_ENV" == "$VENV_DIR" ]]; then
    echo "✅ project ape Account Intelligence virtual environment activated"
    echo "   Python: $(python3 --version)"
    echo "   NotebookLM CLI: $(notebooklm --version 2>&1 | head -1)"
    echo ""
    echo "To deactivate, run: deactivate"
else
    echo "❌ Failed to activate virtual environment"
    return 1 2>/dev/null || exit 1
fi
