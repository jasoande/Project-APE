#!/usr/bin/env python3
"""
NotebookLM Utilities
====================
Common utilities for interacting with NotebookLM CLI
"""

import sys
from pathlib import Path


def get_notebooklm_command() -> str:
    """
    Get the path to the notebooklm CLI binary.

    When running in a virtual environment, notebooklm is in venv/bin/
    and may not be in the system PATH. This function finds it.

    Returns:
        Full path to notebooklm binary, or 'notebooklm' if not found
    """
    # Check if we're in a venv and notebooklm is in the venv's bin
    if hasattr(sys, 'prefix'):
        venv_notebooklm = Path(sys.prefix) / 'bin' / 'notebooklm'
        if venv_notebooklm.exists():
            return str(venv_notebooklm)
    
    # On Mac/Linux, check ~/.project-ape-venv/bin/notebooklm
    home_venv = Path.home() / '.project-ape-venv' / 'bin' / 'notebooklm'
    if home_venv.exists():
        return str(home_venv)

    # Fallback to 'notebooklm' and hope it's in PATH (container mode)
    return 'notebooklm'
