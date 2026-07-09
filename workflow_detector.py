#!/usr/bin/env python3
"""
Workflow Detection Engine
==========================
Analyzes vars.py configuration and determines the appropriate launch command

Usage:
    python3 workflow_detector.py [--json]

Returns:
    JSON object with mode, clients, estimated time, and launch command
"""

import sys
import json
import importlib.util
from pathlib import Path
from typing import Dict, Any


def detect_workflow(vars_module) -> Dict[str, Any]:
    """
    Analyze configuration and return launch parameters.

    Args:
        vars_module: Imported vars.py module

    Returns:
        Dict with keys:
            - mode: str ("fast" or "deep")
            - clients: list of client IDs
            - client_count: int
            - refresh_flag: str ("--refresh" or "")
            - estimated_minutes: int
            - time_range: str (human-readable estimate)
            - command: str (full launch command)
            - drive_enabled: bool
            - dashboard_port: int
    """
    # Get basic configuration
    mode = getattr(vars_module, 'default_mode', 'fast')
    clients = getattr(vars_module, 'clients', [])
    dashboard_port = getattr(vars_module, 'DASHBOARD_PORT', 8765)

    # Check Drive configuration
    drive_config = getattr(vars_module, 'DRIVE_CONFIG', {})
    drive_enabled = drive_config.get('enabled', True)
    cache_enabled = drive_config.get('cache_enabled', True)

    # Determine if refresh needed (disabled cache = always refresh)
    refresh = not cache_enabled

    # Estimate completion time based on mode
    # Times are for parallel execution (all clients run concurrently)
    if mode == "fast":
        # Fast mode: 15-20 minutes for all clients to complete in parallel
        total_time_min = 15
        total_time_max = 20
    else:  # deep mode
        # Deep mode: 45-60 minutes for all clients to complete in parallel
        total_time_min = 45
        total_time_max = 60

    # Format time range
    if len(clients) == 1:
        time_range = f"{total_time_min}-{total_time_max} minutes"
    else:
        # For multiple clients, show total time (parallel execution)
        time_range = f"{total_time_min}-{total_time_max} minutes (all {len(clients)} clients in parallel)"

    # Build launch command
    # Direct execution via main.py (now in project root)
    import sys
    from pathlib import Path

    python_executable = sys.executable  # Use same Python that's running now

    # main.py is now in project root
    main_py_path = 'main.py'

    # Build command arguments
    command_parts = [python_executable, main_py_path, '--mode', mode]

    # Add clients if specified
    if clients:
        command_parts.append('--clients')
        command_parts.extend(clients)  # Add each client as separate argument

    # Add refresh flag if cache disabled
    if not cache_enabled:
        command_parts.append('--refresh')

    # CRITICAL: Skip pre-flight checks when launched from GUI
    # The GUI already validates auth in the configuration wizard
    # Running checks again causes main.py to exit before creating status files
    command_parts.append('--skip-preflight')

    # Join into single command string (for display only)
    command = ' '.join(command_parts)

    # Structured flags for the start-workflow API (no raw command string needed)
    flags = []
    if not cache_enabled:
        flags.append('--refresh')
    flags.append('--skip-preflight')

    # Get client details for display
    client_details = []
    for client_id in clients:
        name = getattr(vars_module, f"{client_id}_name", client_id)
        folder = getattr(vars_module, f"{client_id}_folder", "")
        industry = getattr(vars_module, f"{client_id}_industry", "")

        client_details.append({
            'id': client_id,
            'name': name,
            'folder': folder[:50] + "..." if len(folder) > 50 else folder,
            'industry': industry
        })

    return {
        'mode': mode,
        'clients': clients,
        'client_count': len(clients),
        'client_details': client_details,
        'flags': flags,
        'refresh_flag': '--refresh' if not cache_enabled else '',
        'estimated_minutes_min': total_time_min,
        'estimated_minutes_max': total_time_max,
        'time_range': time_range,
        'command': command,
        'drive_enabled': drive_enabled,
        'cache_enabled': cache_enabled,
        'dashboard_port': dashboard_port,
        'dashboard_url': f"http://localhost:{dashboard_port}"
    }


def load_vars_module(vars_path: Path = None):
    """
    Load vars.py as a Python module.

    Args:
        vars_path: Path to vars.py (defaults to ./vars.py)

    Returns:
        Loaded module object

    Raises:
        FileNotFoundError: If vars.py doesn't exist
        Exception: If vars.py has syntax errors
    """
    if vars_path is None:
        vars_path = Path(__file__).parent / "vars.py"

    if not vars_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {vars_path}\n"
            f"Please create vars.py using the web configuration tool."
        )

    try:
        spec = importlib.util.spec_from_file_location("vars", vars_path)
        vars_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vars_module)
        return vars_module
    except SyntaxError as e:
        raise Exception(
            f"Syntax error in {vars_path}:\n"
            f"  Line {e.lineno}: {e.msg}\n"
            f"Please fix the configuration file."
        )
    except Exception as e:
        raise Exception(
            f"Error loading {vars_path}:\n"
            f"  {str(e)}\n"
            f"Please check the configuration file for errors."
        )


def format_workflow_summary(workflow: Dict[str, Any]) -> str:
    """
    Format workflow details as human-readable text.

    Args:
        workflow: Workflow dict from detect_workflow()

    Returns:
        Formatted multi-line string
    """
    lines = [
        "═══════════════════════════════════════════════",
        "  Account Intelligence - Detected Workflow",
        "═══════════════════════════════════════════════",
        "",
        f"Mode:           {workflow['mode'].upper()}",
        f"Clients:        {workflow['client_count']}",
        f"Estimated Time: {workflow['time_range']}",
        f"Dashboard:      {workflow['dashboard_url']}",
        ""
    ]

    if workflow['client_details']:
        lines.append("Client List:")
        for client in workflow['client_details']:
            lines.append(f"  • {client['name']}")
            if client['industry']:
                lines.append(f"    Industry: {client['industry']}")
        lines.append("")

    if workflow['refresh_flag']:
        lines.append("⚠️  Cache refresh enabled (will re-download all Drive files)")
        lines.append("")

    lines.extend([
        "Command:",
        f"  {workflow['command']}",
        "",
        "═══════════════════════════════════════════════"
    ])

    return "\n".join(lines)


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect Account Intelligence workflow configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Human-readable output
  python3 workflow_detector.py

  # JSON output for scripting
  python3 workflow_detector.py --json

  # Use specific vars.py file
  python3 workflow_detector.py --config /path/to/vars.py
        """
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help="Output as JSON instead of human-readable text"
    )

    parser.add_argument(
        '--config',
        type=Path,
        help="Path to vars.py configuration file (default: ./vars.py)"
    )

    args = parser.parse_args()

    try:
        # Load configuration
        vars_module = load_vars_module(args.config)

        # Detect workflow
        workflow = detect_workflow(vars_module)

        # Output
        if args.json:
            print(json.dumps(workflow, indent=2))
        else:
            print(format_workflow_summary(workflow))

        return 0

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
