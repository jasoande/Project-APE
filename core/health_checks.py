"""Pre-flight validation checks before pipeline execution."""

import importlib.util
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


def check_notebooklm_available(timeout: int = 10) -> Dict:
    """Verify the NotebookLM CLI is installed and responsive."""
    try:
        result = subprocess.run(
            ["notebooklm", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return {"check": "notebooklm_cli", "passed": True, "message": "NotebookLM CLI is available"}
        return {
            "check": "notebooklm_cli",
            "passed": False,
            "message": f"NotebookLM CLI returned error: {result.stderr.strip()}",
        }
    except FileNotFoundError:
        return {"check": "notebooklm_cli", "passed": False, "message": "NotebookLM CLI not found in PATH"}
    except subprocess.TimeoutExpired:
        return {"check": "notebooklm_cli", "passed": False, "message": f"NotebookLM CLI timed out after {timeout}s"}
    except Exception as e:
        return {"check": "notebooklm_cli", "passed": False, "message": f"Unexpected error: {e}"}


def check_notebooklm_auth() -> Dict:
    """Verify NotebookLM authentication credentials are valid."""
    try:
        from core.auth_manager import AuthManager
        auth = AuthManager()
        if auth.is_authenticated():
            return {"check": "notebooklm_auth", "passed": True, "message": "NotebookLM authentication is valid"}
        return {"check": "notebooklm_auth", "passed": False, "message": "NotebookLM authentication not found or expired"}
    except ImportError:
        return {"check": "notebooklm_auth", "passed": False, "message": "AuthManager module not available"}
    except Exception as e:
        return {"check": "notebooklm_auth", "passed": False, "message": f"Auth check error: {e}"}


def check_drive_auth() -> Dict:
    """Verify Google Drive OAuth token exists and contains a token key."""
    token_path = Path.home() / ".project-ape" / "drive_token.json"
    try:
        if not token_path.exists():
            return {"check": "drive_auth", "passed": False, "message": f"Drive token not found at {token_path}"}
        with open(token_path, "r") as f:
            data = json.load(f)
        if "token" in data:
            return {"check": "drive_auth", "passed": True, "message": "Google Drive authentication is valid"}
        return {"check": "drive_auth", "passed": False, "message": "Drive token file missing 'token' key"}
    except json.JSONDecodeError:
        return {"check": "drive_auth", "passed": False, "message": "Drive token file contains invalid JSON"}
    except Exception as e:
        return {"check": "drive_auth", "passed": False, "message": f"Drive auth check error: {e}"}


def check_config_valid(vars_path: Path) -> Dict:
    """Validate vars.py configuration file structure."""
    try:
        if not vars_path.exists():
            return {"check": "config_valid", "passed": False, "message": f"Config file not found: {vars_path}"}

        spec = importlib.util.spec_from_file_location("vars", str(vars_path))
        if spec is None or spec.loader is None:
            return {"check": "config_valid", "passed": False, "message": "Failed to create module spec for config file"}

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        clients = getattr(module, "clients", None)
        if clients is None:
            return {"check": "config_valid", "passed": False, "message": "Config missing 'clients' list"}
        if not isinstance(clients, list) or len(clients) == 0:
            return {"check": "config_valid", "passed": False, "message": "Config 'clients' must be a non-empty list"}

        missing: List[str] = []
        for client_id in clients:
            if not hasattr(module, f"{client_id}_name"):
                missing.append(f"{client_id}_name")
            if not hasattr(module, f"{client_id}_folder"):
                missing.append(f"{client_id}_folder")

        if missing:
            return {
                "check": "config_valid",
                "passed": False,
                "message": f"Config missing attributes: {', '.join(missing)}",
            }

        return {
            "check": "config_valid",
            "passed": True,
            "message": f"Config valid with {len(clients)} client(s): {', '.join(clients)}",
        }
    except Exception as e:
        return {"check": "config_valid", "passed": False, "message": f"Config validation error: {e}"}


def run_preflight_checks(vars_path: Path) -> Dict:
    """Run all pre-flight checks and return a summary."""
    checks = [
        check_notebooklm_available(),
        check_notebooklm_auth(),
        check_drive_auth(),
        check_config_valid(vars_path),
    ]

    all_passed = all(c["passed"] for c in checks)
    passed_count = sum(1 for c in checks if c["passed"])
    total = len(checks)

    summary = f"{passed_count}/{total} checks passed"
    if not all_passed:
        failed = [c["check"] for c in checks if not c["passed"]]
        summary += f" (failed: {', '.join(failed)})"

    return {
        "all_passed": all_passed,
        "checks": checks,
        "summary": summary,
    }
