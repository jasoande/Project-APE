#!/usr/bin/env python3
"""
Project APE - Cross-Platform Launcher
=====================================
Universal launcher for Windows, Linux, and macOS
Double-click or run from terminal to launch the configuration dashboard

This script:
1. Checks if the dashboard server is already running
2. Starts the server if needed (using virtual environment Python)
3. Opens the configuration page in your default browser
"""

import sys
import subprocess
import platform
import time
import webbrowser
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

# Configuration
DASHBOARD_PORT = 8765
CONFIG_URL = f"http://localhost:{DASHBOARD_PORT}/configure"
MAX_WAIT_SECONDS = 10
CHECK_INTERVAL = 0.5

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"


def get_script_directory():
    """Get the directory containing this script, works when double-clicked or run from terminal"""
    return Path(__file__).parent.resolve()


def get_venv_python():
    """Get path to Python executable in virtual environment (platform-aware)"""
    home = Path.home()
    venv_dir = home / ".project-ape-venv"

    if IS_WINDOWS:
        python_path = venv_dir / "Scripts" / "python.exe"
    else:
        python_path = venv_dir / "bin" / "python3"

    return python_path


def is_server_running():
    """Check if the dashboard server is already running"""
    try:
        with urlopen(CONFIG_URL, timeout=2) as response:
            return response.status == 200
    except (URLError, TimeoutError, OSError):
        return False


def start_server():
    """Start the dashboard server in background"""
    script_dir = get_script_directory()
    venv_python = get_venv_python()
    server_script = script_dir / "dashboard" / "server.py"

    # Verify virtual environment exists
    if not venv_python.exists():
        print("❌ Error: Virtual environment not found")
        print(f"   Expected: {venv_python}")
        print("\n⚠️  Please run the setup script first:")
        if IS_WINDOWS:
            print("   Note: Setup script requires bash shell (Git Bash, WSL, or Cygwin)")
            print("   bash ./setup-environment.sh")
        else:
            print("   ./setup-environment.sh")
        sys.exit(1)

    # Verify server script exists
    if not server_script.exists():
        print(f"❌ Error: Dashboard server not found at {server_script}")
        sys.exit(1)

    # Start server in background (platform-specific)
    try:
        if IS_WINDOWS:
            # Windows: Use CREATE_NEW_PROCESS_GROUP and CREATE_NO_WINDOW
            subprocess.Popen(
                [str(venv_python), str(server_script)],
                cwd=str(script_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
            )
        else:
            # Unix: Use nohup-style background execution
            subprocess.Popen(
                [str(venv_python), str(server_script)],
                cwd=str(script_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

        return True
    except Exception as e:
        print(f"❌ Failed to start dashboard server: {e}")
        return False


def wait_for_server_ready():
    """Wait for server to become ready (max wait time)"""
    print("⏳ Starting dashboard server...")

    max_checks = int(MAX_WAIT_SECONDS / CHECK_INTERVAL)
    for i in range(max_checks):
        if is_server_running():
            print("✅ Dashboard server is ready")
            return True
        time.sleep(CHECK_INTERVAL)

    return False


def open_browser():
    """Open the configuration page in default browser (cross-platform)"""
    try:
        webbrowser.open(CONFIG_URL)
        print(f"🌐 Opening browser: {CONFIG_URL}")
        return True
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print(f"   Please manually navigate to: {CONFIG_URL}")
        return False


def main():
    """Main launcher logic"""
    print("=" * 70)
    print("PROJECT APE - Account Planning Engine")
    print("=" * 70)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Dashboard: {CONFIG_URL}")
    print()

    # Check if server is already running
    if is_server_running():
        print("✅ Dashboard server is already running")
        open_browser()
        print()
        print("Dashboard is ready! Configure your clients and start workflows.")
        sys.exit(0)

    # Server not running, start it
    print("🚀 Server not detected, starting new instance...")

    if not start_server():
        print("\n❌ Failed to start dashboard server")
        print("   Check that the virtual environment is set up correctly")
        sys.exit(1)

    # Wait for server to be ready
    if not wait_for_server_ready():
        print("\n❌ Server did not start within timeout period")
        print(f"   Waited {MAX_WAIT_SECONDS} seconds")
        print("\n💡 Troubleshooting steps:")
        print("   1. Check if port 8765 is already in use")
        print("   2. Verify virtual environment: ~/.project-ape-venv")
        print("   3. Try running manually: python dashboard/server.py")
        sys.exit(1)

    # Open browser
    open_browser()

    print()
    print("=" * 70)
    print("✅ SUCCESS - Dashboard is ready!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Complete environment setup (if not already done)")
    print("  2. Configure your clients")
    print("  3. Launch your first workflow")
    print()
    print("The server is running in the background.")
    print("Close your browser to stop using the dashboard (server keeps running).")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Launcher interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
