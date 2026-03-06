#!/usr/bin/env python3
"""
🚀 COMPLETE SYSTEM ORCHESTRATOR
Starts all services in proper sequence: API → Continuous Hive → Dashboard
Coordinates all system components into unified operation
"""

import asyncio
import subprocess
import sys
import time
import signal
from pathlib import Path
from typing import List, Optional
import json
from datetime import datetime
import os


# ═══════════════════════════════════════════════════════════════════
# SERVICE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

class ServiceOrchestrator:
    """
    Manages startup, health, and coordination of all system services
    """
    
    def __init__(self):
        self.services: dict = {}
        self.processes: dict = {}
        self.health_status: dict = {}
        self.logs_dir = Path("logs/orchestration")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
    def register_service(self, name: str, command: List[str], port: int, 
                        startup_wait: int = 3, is_critical: bool = True):
        """Register a service to be managed"""
        self.services[name] = {
            "command": command,
            "port": port,
            "startup_wait": startup_wait,
            "is_critical": is_critical,
            "status": "not_started"
        }
    
    async def start_service(self, name: str) -> bool:
        """Start a single service"""
        service = self.services.get(name)
        if not service:
            print(f"❌ Unknown service: {name}")
            return False
        
        print(f"\n🚀 Starting {name}...")
        
        try:
            # Create log file
            log_path = self.logs_dir / f"{name}.log"
            log_file = open(log_path, "w")
            
            # Start process
            process = subprocess.Popen(
                service["command"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            self.processes[name] = process
            service["status"] = "starting"
            
            # Wait for startup
            await asyncio.sleep(service["startup_wait"])
            
            # Check if process is still alive
            if process.poll() is None:
                service["status"] = "running"
                self.health_status[name] = "✅ running"
                print(f"✅ {name} started (PID: {process.pid}, LOG: {log_path})")
                return True
            else:
                service["status"] = "failed"
                self.health_status[name] = "❌ failed to start"
                print(f"❌ {name} failed to start")
                return False
                
        except Exception as e:
            service["status"] = "error"
            self.health_status[name] = f"❌ error: {e}"
            print(f"❌ Error starting {name}: {e}")
            return False
    
    async def start_all(self) -> bool:
        """Start all registered services in order"""
        print("\n" + "="*60)
        print("🌐 SYSTEM ORCHESTRATION STARTING")
        print("="*60)
        
        all_critical_ok = True
        startup_order = [
            ("unified_api", "API Server"),
            ("continuous_hive", "Continuous Research"),
            ("dashboard", "Streamlit Dashboard")
        ]
        
        for service_name, display_name in startup_order:
            if service_name not in self.services:
                print(f"⏭️  Skipping {display_name} (not registered)")
                continue
                
            success = await self.start_service(service_name)
            
            if not success and self.services[service_name]["is_critical"]:
                all_critical_ok = False
                print(f"🛑 Critical service {service_name} failed!")
        
        return all_critical_ok
    
    async def health_check(self) -> dict:
        """Check health of all running services"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        for name, process in self.processes.items():
            if process.poll() is None:
                status["services"][name] = "running"
            else:
                status["services"][name] = "dead"
        
        return status
    
    def display_dashboard(self):
        """Display system status dashboard"""
        print("\n" + "="*60)
        print("📊 SYSTEM STATUS DASHBOARD")
        print("="*60)
        
        for name, status_text in self.health_status.items():
            print(f"{name:20} → {status_text}")
        
        print("\n" + "-"*60)
        print("📝 ENDPOINT SUMMARY:")
        print("-"*60)
        print("🔬 Research API      → http://localhost:8000")
        print("📊 API Documentation → http://localhost:8000/docs")
        print("📈 Dashboard         → http://localhost:8501")
        print("📋 Logs Directory    → logs/orchestration/")
        print("="*60 + "\n")
    
    def shutdown(self):
        """Gracefully shutdown all services"""
        print("\n" + "="*60)
        print("🛑 SHUTTING DOWN SYSTEM")
        print("="*60)
        
        for name, process in self.processes.items():
            print(f"Stopping {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️  {name} force-killed")
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
        
        print("🛑 All services stopped\n")


# ═══════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATION
# ═══════════════════════════════════════════════════════════════════

async def main():
    """Main orchestration flow"""
    
    # Create orchestrator
    orchestrator = ServiceOrchestrator()
    
    # Register services
    orchestrator.register_service(
        "unified_api",
        ["python", "-m", "uvicorn", "src.unified_research_api:app", 
         "--host", "0.0.0.0", "--port", "8000", "--reload"],
        port=8000,
        startup_wait=5,
        is_critical=True
    )
    
    orchestrator.register_service(
        "continuous_hive",
        ["python", "hive_continuous.py"],
        port=None,
        startup_wait=3,
        is_critical=False
    )
    
    orchestrator.register_service(
        "dashboard",
        ["streamlit", "run", "frontend/sovereign_dashboard.py", 
         "--server.port=8501", "--logger.level=error"],
        port=8501,
        startup_wait=7,
        is_critical=True
    )
    
    # Start all services
    success = await orchestrator.start_all()
    
    if not success:
        print("\n⚠️  Some critical services failed to start")
        orchestrator.shutdown()
        sys.exit(1)
    
    # Display dashboard
    orchestrator.display_dashboard()
    
    # Keep running and monitor
    print("🔄 Monitoring services... (Press Ctrl+C to stop)\n")
    
    try:
        while True:
            await asyncio.sleep(30)
            status = await orchestrator.health_check()
            
            # Check for dead processes and restart if needed
            for name, service_status in status["services"].items():
                if service_status == "dead":
                    print(f"⚠️  {name} died, restarting...")
                    if orchestrator.services[name]["is_critical"]:
                        await orchestrator.start_service(name)
    
    except KeyboardInterrupt:
        print("\n")
        orchestrator.shutdown()
        sys.exit(0)


# ═══════════════════════════════════════════════════════════════════
# VALIDATION & STARTUP
# ═══════════════════════════════════════════════════════════════════

def validate_environment():
    """Validate that all required files and dependencies exist"""
    print("\n" + "="*60)
    print("🔍 ENVIRONMENT VALIDATION")
    print("="*60)
    
    required_files = [
        "src/unified_research_api.py",
        "src/data/unified_db.py",
        "hive_continuous.py",
        "frontend/sovereign_dashboard.py",
        "src/core/graph_utils.py",
        "src/agents/hive_council.py",
    ]
    
    all_ok = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING!")
            all_ok = False
    
    print("="*60)
    return all_ok


async def async_main():
    """Async entry point"""
    # Validate environment
    if not validate_environment():
        print("\n❌ Environment validation failed!")
        sys.exit(1)
    
    # Start orchestration
    await main()


def sync_main():
    """Sync entry point for those without asyncio experience"""
    asyncio.run(async_main())


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "validate":
            validate_environment()
        elif command == "status":
            print("\n⚠️  Use './start_hive.sh status' to check system status")
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python orchestrator.py              # Start all services")
            print("  python orchestrator.py validate     # Validate environment")
    else:
        sync_main()
