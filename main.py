#!/usr/bin/env python3
"""
Account Intelligence - Account Planning Engine
======================================
Main multi-process orchestrator

Features:
- Multi-process architecture for parallel execution
- Flask dashboard with real-time updates
- Complete pipeline with PDF consolidation and research
- Dual-mode execution (Fast/Deep)

IMPORTANT: This script requires the Account Intelligence virtual environment.
Use one of these methods to run:
  1. ./run-workflow.sh fast              (recommended)
  2. source ~/.project-ape-venv/bin/activate && python3 main.py fast
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

# SSL is always enabled
DASHBOARD_PROTOCOL = "https"
DASHBOARD_URL = f"https://localhost:{DASHBOARD_PORT}"

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
        self._log_handles = []
        self.start_time = None
        self.run_id = run_id or str(int(time.time()))

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

        # Kill any existing process on the dashboard port
        try:
            import subprocess
            result = subprocess.run(
                ['lsof', '-ti', f':{DASHBOARD_PORT}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        logger.info(f"   Killing stale process on port {DASHBOARD_PORT} (PID: {pid})")
                        subprocess.run(['kill', '-9', pid], timeout=2)
                    except:
                        pass
                time.sleep(1)
        except:
            pass  # lsof might not be available on all systems

        # Always use gevent server (supports HTTPS)
        dashboard_script = SCRIPT_DIR / "dashboard" / "server_gevent.py"
        dashboard_log = LOGS_DIR / "dashboard.log"

        log_handle = open(dashboard_log, 'w', buffering=1)
        self._log_handles.append(log_handle)

        self.dashboard_process = subprocess.Popen(
            [sys.executable, '-u', str(dashboard_script)],  # -u for unbuffered Python output
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            env={**subprocess.os.environ, 'PYTHONUNBUFFERED': '1'}  # Force unbuffered
        )

        # Smart polling: Check server readiness with increasing intervals
        # This replaces hardcoded 3-second sleep with adaptive polling (50-60% faster)
        time.sleep(0.5)  # Initial settle time
        dashboard_running = False
        max_retries = 20  # Max ~10 seconds total (0.5 + 20*0.3 + backoff)

        import urllib.request
        import ssl

        # For HTTPS with self-signed certs, disable verification
        ssl_context = ssl._create_unverified_context()

        for attempt in range(max_retries):
            try:
                # Use lightweight /ping endpoint for fast startup validation
                urllib.request.urlopen(
                    f"{DASHBOARD_URL}/ping",
                    timeout=0.5,
                    context=ssl_context
                )
                dashboard_running = True
                logger.info(f"   Dashboard responded after {0.5 + attempt * 0.3:.1f}s")
                break
            except:
                if attempt < max_retries - 1:
                    time.sleep(0.3)  # Progressive polling every 300ms
                else:
                    dashboard_running = False

        if not dashboard_running:
            logger.error(f"   ❌ Dashboard failed to start on port {DASHBOARD_PORT}")
            logger.error(f"   Check {dashboard_log} for errors")
            # Read first few lines of error log
            try:
                with open(dashboard_log, 'r') as f:
                    error_lines = f.readlines()[-5:]
                    for line in error_lines:
                        logger.error(f"      {line.rstrip()}")
            except:
                pass
            raise RuntimeError(f"Dashboard failed to start - check {dashboard_log}")

        logger.info(f"   URL: {DASHBOARD_URL}")
        logger.info("   ✅ Dashboard server running")

        # Open in browser
        try:
            webbrowser.open(DASHBOARD_URL)
            logger.info("   ✅ Dashboard opened in browser")
        except:
            logger.warning("   Could not open browser automatically")
            logger.info(f"   Please open: {dashboard_url}")

    def start_client_process(self, client_id: str, mode: str, refresh: bool = False) -> subprocess.Popen:
        """Start a single client process."""
        log_file = LOGS_DIR / f"{client_id}.log"
        status_file = STATUS_DIR / f"{client_id}.json"

        client_name = getattr(config, f"{client_id}_name", client_id)

        # Logging handled by caller in wave launch code
        log_handle = open(log_file, 'w')
        self._log_handles.append(log_handle)

        # Build command
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "core" / "client_pipeline.py"),
            client_id,
            "--mode", mode,
            "--status-file", str(status_file)
        ]

        if refresh:
            cmd.append("--refresh")

        if hasattr(self, '_resume') and self._resume:
            cmd.append("--resume")

        # Start process
        process = subprocess.Popen(
            cmd,
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

        # Terminate dashboard with proper signal handling
        if self.dashboard_process and self.dashboard_process.poll() is None:
            logger.info("   Stopping dashboard server...")
            self.dashboard_process.terminate()
            time.sleep(2)
            if self.dashboard_process.poll() is None:
                logger.warning("   Dashboard didn't stop gracefully, forcing...")
                self.dashboard_process.kill()

        # Close all log file handles to prevent FD leaks
        for handle in self._log_handles:
            try:
                handle.close()
            except Exception:
                pass
        self._log_handles.clear()

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
    print(f"  Version: 4.1.0 - Security, Checkpoint/Resume, Health Checks")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


def main():
    """Main orchestrator entry point."""
    # Global manager for signal handler
    global_manager = None

    # Signal handler for graceful shutdown
    def signal_handler(sig, frame):
        logger.warning(f"\n⚠️  Received signal {sig}")
        if global_manager:
            logger.info("Initiating graceful shutdown...")
            global_manager.cleanup()
        import os
        os._exit(1)

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(
        description="Account Intelligence - Account Planning Engine",
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
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force refresh Google Drive cache (ignore TTL)"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last checkpoint (skip completed phases)"
    )
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip pre-flight health checks"
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
    logger.info(f"   Resume: {'Yes' if args.resume else 'No'}")

    # Pre-flight health checks
    if not args.skip_preflight:
        try:
            from core.health_checks import run_preflight_checks
            logger.info("\n🔍 Running pre-flight checks...")
            preflight = run_preflight_checks(SCRIPT_DIR / "vars.py")
            for check in preflight['checks']:
                status_icon = "✅" if check['passed'] else "❌"
                logger.info(f"   {status_icon} {check['check']}: {check['message']}")
            if not preflight['all_passed']:
                logger.error("\n❌ Pre-flight checks failed. Use --skip-preflight to bypass.")
                sys.exit(1)
            logger.info("   ✅ All pre-flight checks passed")
        except ImportError:
            logger.warning("   ⚠️  Health checks module not available, skipping")

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
    manager._resume = args.resume
    global_manager = manager

    logger.info(f"\n🆔 Run ID: {run_id}")

    # Write PID file for workflow stop button
    pid_file = STATUS_DIR / '.workflow_pid'
    with open(pid_file, 'w') as f:
        json.dump({
            'pid': subprocess.os.getpid(),
            'run_id': run_id,
            'started_at': time.time(),
            'mode': args.mode,
            'clients': clients
        }, f, indent=2)
    logger.info(f"   📝 Workflow PID: {subprocess.os.getpid()}")

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
            if args.refresh:
                logger.info(f"   🔄 Force Refresh: ENABLED")
            logger.info(f"   Log: {client_id}.log")

            process = manager.start_client_process(client_id, args.mode, args.refresh)
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

        # Send completion notification
        try:
            from core.notification_manager import notify_completion
            results['duration_minutes'] = elapsed / 60
            notify_completion(config, results)
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"   ⚠️  Notification failed: {e}")

        if not args.no_dashboard:
            logger.info(f"\n📊 Dashboard: {DASHBOARD_URL}")
            logger.info("   Dashboard will remain running for 5 minutes after completion")
            logger.info("   Press Ctrl+C to stop immediately")

            # Keep dashboard running for 5 minutes after completion
            # This gives users time to review results before container shuts down
            try:
                shutdown_delay = 300  # 5 minutes
                logger.info(f"   ⏰ Auto-shutdown in {shutdown_delay//60} minutes...")
                time.sleep(shutdown_delay)
                logger.info("\n⏰ Auto-shutdown timer expired. Stopping container...")
            except KeyboardInterrupt:
                logger.info("\n⌨️  Ctrl+C detected. Stopping immediately...")
                pass

        # Cleanup
        manager.cleanup()

        # Remove PID file
        pid_file = STATUS_DIR / '.workflow_pid'
        pid_file.unlink(missing_ok=True)

        # Additional step: Try to trigger dashboard shutdown via API
        # This is a belt-and-suspenders approach to ensure dashboard stops
        if not args.no_dashboard:
            try:
                import urllib.request
                import ssl
                logger.info("   Requesting dashboard shutdown via API...")
                req = urllib.request.Request(
                    f"{DASHBOARD_URL}/api/shutdown",
                    method='POST'
                )
                ssl_context = ssl._create_unverified_context()
                urllib.request.urlopen(req, timeout=2, context=ssl_context)
            except Exception as e:
                # Ignore errors - dashboard might already be down
                logger.debug(f"   Dashboard API call failed (expected): {e}")

        # Exit with proper code
        # Use os._exit() to ensure immediate termination without running cleanup handlers
        # This ensures the container actually stops instead of hanging
        exit_code = 0 if results['failed'] == 0 else 1
        logger.info(f"\n👋 Exiting with code {exit_code}")

        import os
        os._exit(exit_code)

    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        manager.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
