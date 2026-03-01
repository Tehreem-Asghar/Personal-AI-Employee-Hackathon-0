import os
import sys
import time
import logging
import psutil
import subprocess
from pathlib import Path
from typing import Dict

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.paths import find_vault_root
from src.utils.notifications import send_alert

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GuardianWatchdog")

class Watchdog:
    """
    Guardian Angel for the AI Employee.
    Monitors critical processes and restarts them if they fail.
    """
    def __init__(self):
        self.vault_root = find_vault_root()
        self.venv_python = sys.executable  # Use current python executable (in venv)
        
        # Define critical processes to monitor
        self.processes = {
            "orchestrator": {
                "cmd": ["uv", "run", "python", "src/agents/orchestrator.py"],
                "pid_file": self.vault_root / ".system" / "orchestrator.pid"
            },
            "gmail_watcher": {
                "cmd": ["uv", "run", "python", "src/watchers/gmail_watcher.py"],
                "pid_file": self.vault_root / ".system" / "gmail_watcher.pid"
            },
            "fs_watcher": {
                "cmd": ["uv", "run", "python", "src/watchers/fs_watcher.py"],
                "pid_file": self.vault_root / ".system" / "fs_watcher.pid"
            }
            # Add other watchers as needed
        }

    def start_process(self, name: str, config: Dict) -> int:
        """Starts a process and records its PID."""
        try:
            logger.info(f"Starting {name}...")
            # Use subprocess.Popen to start independent process
            proc = subprocess.Popen(
                config["cmd"], 
                cwd=str(Path(__file__).parent.parent.parent),
                stdout=subprocess.DEVNULL,  # Redirect output to avoid clutter
                stderr=subprocess.DEVNULL
            )
            
            # Save PID
            config["pid_file"].parent.mkdir(parents=True, exist_ok=True)
            config["pid_file"].write_text(str(proc.pid), encoding='utf-8')
            
            logger.info(f"Started {name} with PID {proc.pid}")
            return proc.pid
        except Exception as e:
            logger.error(f"Failed to start {name}: {e}")
            return 0

    def is_running(self, pid: int) -> bool:
        """Checks if a PID is running."""
        try:
            p = psutil.Process(pid)
            return p.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            return False

    def check_health(self):
        """Checks all monitored processes and restarts dead ones."""
        for name, config in self.processes.items():
            pid = 0
            if config["pid_file"].exists():
                try:
                    pid = int(config["pid_file"].read_text().strip())
                except:
                    pid = 0
            
            if pid > 0 and self.is_running(pid):
                # Healthy
                pass
            else:
                logger.warning(f"Process {name} is DEAD (PID {pid}). Restarting...")
                self.start_process(name, config)
                
                send_alert(
                    subject=f"Watchdog Restart: {name}",
                    message=f"The process {name} was found dead and has been restarted."
                )

    def run(self):
        logger.info("Guardian Watchdog started. Monitoring system health...")
        # Initial start
        for name in self.processes:
            self.check_health()
            
        while True:
            self.check_health()
            time.sleep(60) # Check every minute

if __name__ == "__main__":
    watchdog = Watchdog()
    try:
        watchdog.run()
    except KeyboardInterrupt:
        logger.info("Watchdog stopped by user.")
