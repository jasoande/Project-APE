#!/usr/bin/env python3
"""
Project APE - Account Planning Engine
======================================
Main multi-process orchestrator

Features:
- Multi-process architecture for parallel execution
- Flask dashboard with real-time updates
- Complete pipeline with PDF consolidation and research
- Dual-mode execution (Fast/Deep)
"""

import subprocess
import sys
import time
import webbrowser
import json
import argparse
import signal
import logging
# import random  # No longer needed - removed wave launching
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import importlib.util
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==============================================================================
# CONFIGURATION
# ==============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

# Load configuration
spec = importlib.util.spec_from_file_location("config", SCRIPT_DIR / "vars.py")
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

# Use paths from config (for container compatibility)
STATUS_DIR = getattr(config, 'STATUS_DIR', SCRIPT_DIR / ".multi_process_status")
LOGS_DIR = getattr(config, 'LOGS_DIR', SCRIPT_DIR / "logs")
DASHBOARD_PORT = config.DASHBOARD_PORT

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ==============================================================================
# PROCESS MANAGEMENT
# ==============================================================================

class ProcessManager:
    """Manages client processes and dashboard server."""

    def __init__(self, run_id: str = None):
        self.client_processes: List[subprocess.Popen] = []
        self.dashboard_process: subprocess.Popen = None
        self.start_time = None
        self.run_id = run_id or str(int(time.time()))  # Unique ID for this run

    def initialize_status_file(self, client_id: str, mode: str):
        """Create initial status file for a client."""
        STATUS_DIR.mkdir(exist_ok=True)
        status_file = STATUS_DIR / f"{client_id}.json"

        client_name = getattr(config, f"{client_id}_name", client_id)

        status_data = {
            "name": client_name,
            "token": client_id,
            "step": "Initializing...",
            "progress": 0,
            "status": "PENDING",
            "notebook_id": None,
            "mode": mode,
            "last_update": time.time(),
            "start_time": time.time(),  # Persist start time for accurate elapsed calculation
            "quality_score": None,
            "plan_link": None,
            "log_file": str(LOGS_DIR / f"{client_id}.log"),
            "run_id": self.run_id  # Add unique run ID
        }

        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)

        logger.info(f"   ✅ Initialized: {client_name}")

    def start_dashboard(self):
        """Start Flask dashboard server."""
        logger.info("\n📊 Starting dashboard server...")

        dashboard_script = SCRIPT_DIR / "dashboard" / "server.py"

        self.dashboard_process = subprocess.Popen(
            [sys.executable, str(dashboard_script)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Wait for server to start
        time.sleep(3)

        dashboard_url = f"http://localhost:{DASHBOARD_PORT}"
        logger.info(f"   URL: {dashboard_url}")

        # Open in browser
        try:
            webbrowser.open(dashboard_url)
            logger.info("   ✅ Dashboard opened in browser")
        except:
            logger.warning("   Could not open browser automatically")
            logger.info(f"   Please open: {dashboard_url}")

    def start_client_process(self, client_id: str, mode: str) -> subprocess.Popen:
        """Start a single client process."""
        log_file = LOGS_DIR / f"{client_id}.log"
        status_file = STATUS_DIR / f"{client_id}.json"

        client_name = getattr(config, f"{client_id}_name", client_id)

        # Logging handled by caller in wave launch code
        # Open log file
        log_handle = open(log_file, 'w')

        # Start process
        process = subprocess.Popen(
            [
                sys.executable,
                str(SCRIPT_DIR / "core" / "client_pipeline.py"),
                client_id,
                "--mode", mode,
                "--status-file", str(status_file)
            ],
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            cwd=str(SCRIPT_DIR)
        )

        return process

    def monitor_processes(self):
        """Monitor all client processes until complete."""
        logger.info("\n" + "="*60)
        logger.info("⏳ Monitoring client processes...")
        logger.info("="*60)

        try:
            while True:
                # Check if all processes finished
                all_done = all(p.poll() is not None for p in self.client_processes)

                if all_done:
                    break

                time.sleep(5)

        except KeyboardInterrupt:
            logger.warning("\n⚠️  Keyboard interrupt detected")
            self.cleanup()
            sys.exit(1)

    def get_results(self) -> Dict:
        """Get final results from all clients."""
        results = {
            'total': len(self.client_processes),
            'successful': 0,
            'failed': 0,
            'clients': []
        }

        for i, process in enumerate(self.client_processes):
            client_info = {
                'index': i,
                'exit_code': process.returncode,
                'success': process.returncode == 0
            }

            if client_info['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1

            results['clients'].append(client_info)

        return results

    def cleanup(self):
        """Cleanup processes."""
        logger.info("\n🧹 Cleaning up...")

        # Terminate client processes
        for process in self.client_processes:
            if process.poll() is None:
                process.terminate()
                time.sleep(1)
                if process.poll() is None:
                    process.kill()

        # Terminate dashboard
        if self.dashboard_process and self.dashboard_process.poll() is None:
            self.dashboard_process.terminate()
            time.sleep(1)
            if self.dashboard_process.poll() is None:
                self.dashboard_process.kill()

        logger.info("   ✅ Cleanup complete")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def print_banner():
    """Print startup banner."""
    print("\n" + "="*70)
    print("  PROJECT APE - ACCOUNT PLANNING ENGINE")
    print("  AI-Powered Enterprise Account Planning Automation")
    print("="*70)
    print(f"  Version: 3.2.0 - Simplified Dependencies Release")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


def main():
    """Main orchestrator entry point."""
    parser = argparse.ArgumentParser(
        description="Project APE - Account Planning Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--mode",
        choices=["fast", "deep", "update"],
        default="fast",
        help="Execution mode: fast (10-15min), deep (35-40min), update (refresh existing, 5-10min)"
    )
    parser.add_argument(
        "--clients",
        nargs="+",
        help="Specific clients to run (default: all from vars.py)"
    )
    parser.add_argument(
        "--no-dashboard",
        action="store_true",
        help="Disable dashboard server"
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Get clients list
    clients = args.clients if args.clients else config.clients

    if not clients:
        logger.error("❌ No clients defined. Check vars.py or pass --clients")
        sys.exit(1)

    logger.info(f"📋 Configuration:")
    logger.info(f"   Mode: {args.mode.upper()}")
    logger.info(f"   Clients: {len(clients)}")
    logger.info(f"   Dashboard: {'Disabled' if args.no_dashboard else 'Enabled'}")

    # Create directories
    STATUS_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

    # Clean up old status files from previous runs
    logger.info("\n🧹 Cleaning up old status files...")
    if STATUS_DIR.exists():
        for old_status in STATUS_DIR.glob("*.json"):
            old_status.unlink()
            logger.info(f"   Removed: {old_status.name}")

    # Initialize process manager with unique run ID
    run_id = str(int(time.time()))
    manager = ProcessManager(run_id=run_id)
    manager.start_time = time.time()

    logger.info(f"\n🆔 Run ID: {run_id}")

    try:
        # Initialize status files
        logger.info("\n📝 Initializing status files...")
        for client_id in clients:
            manager.initialize_status_file(client_id, args.mode)

        # Start dashboard
        if not args.no_dashboard:
            manager.start_dashboard()

        # Start client processes
        logger.info("\n🚀 Launching client processes...")

        # Determine stagger delay based on mode
        # Reduced from 15/5 to 10/2 for faster initialization
        stagger_delay = 10 if args.mode == "deep" else 2

        # Launch clients with stagger to avoid initial collision
        for i, client_id in enumerate(clients):
            logger.info(f"\n🚀 Starting: {getattr(config, f'{client_id}_name', client_id)}")
            logger.info(f"   Mode: {args.mode.upper()}")
            logger.info(f"   Log: {client_id}.log")

            process = manager.start_client_process(client_id, args.mode)
            manager.client_processes.append(process)

            # Stagger launches to prevent simultaneous starts
            if i < len(clients) - 1:  # Don't wait after the last client
                logger.info(f"   ⏳ Waiting {stagger_delay}s before next client...")
                time.sleep(stagger_delay)

        # Monitor processes
        manager.monitor_processes()

        # Get results
        results = manager.get_results()
        elapsed = time.time() - manager.start_time

        # Print summary
        logger.info("\n" + "="*60)
        logger.info("🏁 PIPELINE COMPLETE")
        logger.info("="*60)
        logger.info(f"   Total Clients: {results['total']}")
        logger.info(f"   ✅ Successful: {results['successful']}")
        logger.info(f"   ❌ Failed: {results['failed']}")
        logger.info(f"   ⏱️  Duration: {elapsed/60:.1f} minutes")
        logger.info("="*60)

        if not args.no_dashboard:
            logger.info(f"\n📊 Dashboard: http://localhost:{DASHBOARD_PORT}")
            logger.info("   Dashboard will remain running for review")
            logger.info("   Press Ctrl+C to stop")

            # Keep dashboard running
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                pass

        # Cleanup
        manager.cleanup()

        # Exit code
        sys.exit(0 if results['failed'] == 0 else 1)

    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        manager.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
