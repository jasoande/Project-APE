#!/usr/bin/env python3
"""Utility to get notebooklm command path."""
import sys
from pathlib import Path

# Check if we're in a venv and notebooklm is in the venv's bin
if hasattr(sys, 'prefix'):
    venv_notebooklm = Path(sys.prefix) / 'bin' / 'notebooklm'
    if venv_notebooklm.exists():
        NOTEBOOKLM_CMD = str(venv_notebooklm)
    else:
        # Try home venv
        home_venv = Path.home() / '.project-ape-venv' / 'bin' / 'notebooklm'
        NOTEBOOKLM_CMD = str(home_venv) if home_venv.exists() else 'notebooklm'
else:
    NOTEBOOKLM_CMD = 'notebooklm'
