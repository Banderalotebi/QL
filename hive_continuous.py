#!/usr/bin/env python3
"""
🏛️ CONTINUOUS HIVE OPERATION - Background Runner
Runs the hive indefinitely with monitoring and recovery
"""
import time
import logging
import signal
import sys
from pathlib import Path
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspaces/QL/logs/hive_continuous.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from src.agents.hive_council import get_hive_council
from src.core.graph_utils import compile_graph
from src.core.state import ResearchState
from src.utils.arabic import MUQATTAAT_SURAH_NUMBERS


class ContinuousHiveRunner:
    """
    Runs the hive continuously with:
    - Automatic recovery on failures
    - Periodic state saves
    - Health monitoring
    - Graceful shutdown
    """
    
    def __init__(self, batch_size=3, loop_interval=300):
        """
        Initialize continuous runner
        
        Args:
            batch_size: Number of surahs to analyze per batch
            loop_interval: Seconds between batch runs (default: 5 min)
        """
        self.batch_size = batch_size
        self.loop_interval = loop_interval
        self.hive = get_hive_council()
        self.graph = compile_graph()
        self.running = True
        self.batch_count = 0
        self.error_count = 0
        
        # Create logs directory
        Path('/workspaces/QL/logs').mkdir(exist_ok=True)
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("🏛️  Continuous Hive Runner initialized")
        logger.info(f"   Batch size: {batch_size} surahs")
        logger.info(f"   Loop interval: {loop_interval} seconds")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"📊 Received signal {signum} - shutting down gracefully...")
        self.running = False
        self._save_final_state()
        sys.exit(0)

    def _save_final_state(self):
        """Save hive state before shutdown"""
        try:
            self.hive.save_hive_state()
            logger.info("✅ Hive state saved before shutdown")
        except Exception as e:
            logger.error(f"❌ Error saving state: {e}")

    def run_batch(self, surah_list):
        """
        Run a batch of surah analyses
        
        Args:
            surah_list: List of surah numbers to analyze
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 Starting batch {self.batch_count + 1}")
        logger.info(f"   Analyzing {len(surah_list)} surahs: {surah_list}")
        logger.info(f"{'='*80}")
        
        try:
            initial_state: ResearchState = {
                "surah_numbers": surah_list,
                "focus": "muqattaat",
                "raw_hypotheses": [],
                "errors": []
            }
            
            # Run the pipeline
            final_state = self.graph.invoke(initial_state)
            
            # Extract results
            theories = final_state.get("ranked_theories", [])
            hive_status = self.hive.get_hive_status()
            
            logger.info(f"✅ Batch {self.batch_count + 1} completed")
            logger.info(f"   Theories found: {len(theories)}")
            logger.info(f"   Supervisions: {hive_status['total_supervisions']}")
            logger.info(f"   Error count: {self.error_count}")
            
            self.batch_count += 1
            
            # Save state periodically
            if self.batch_count % 3 == 0:
                self.hive.save_hive_state()
                logger.info("💾 Periodic state save completed")
            
            return True
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ Error in batch {self.batch_count + 1}: {e}")
            
            # Auto-recovery
            if self.error_count <= 3:
                logger.info(f"⚠️  Attempting recovery ({self.error_count}/3)...")
                time.sleep(10)  # Wait before retry
                return False
            else:
                logger.error("❌ Max errors exceeded - stopping")
                return False

    def run_continuous(self):
        """
        Main continuous operation loop
        Cycles through batches of surahs indefinitely
        """
        all_surahs = list(MUQATTAAT_SURAH_NUMBERS)
        
        logger.info(f"🏛️  Starting continuous hive operation")
        logger.info(f"   Total surahs available: {len(all_surahs)}")
        logger.info(f"   Batch size: {self.batch_size}")
        logger.info(f"   Batches per cycle: {len(all_surahs) // self.batch_size}")
        
        batch_index = 0
        
        while self.running:
            try:
                # Get next batch
                start_idx = (batch_index * self.batch_size) % len(all_surahs)
                end_idx = min(start_idx + self.batch_size, len(all_surahs))
                current_batch = all_surahs[start_idx:end_idx]
                
                # Run batch
                success = self.run_batch(current_batch)
                
                if success:
                    batch_index += 1
                    
                    # Wait before next batch
                    if self.running:
                        logger.info(f"⏳ Waiting {self.loop_interval}s before next batch...")
                        time.sleep(self.loop_interval)
                
            except KeyboardInterrupt:
                logger.info("⏸️  Keyboard interrupt detected")
                self.running = False
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                self.error_count += 1
                if self.error_count > 10:
                    logger.error("Too many errors, shutting down")
                    self.running = False
                time.sleep(30)  # Wait before retry
        
        # Cleanup
        logger.info("🛑 Continuous operation stopped")
        self._save_final_state()

    def get_status(self) -> dict:
        """Get runner status"""
        hive_status = self.hive.get_hive_status()
        
        return {
            "running": self.running,
            "batch_count": self.batch_count,
            "error_count": self.error_count,
            "uptime_minutes": (time.time() - self.start_time) / 60 if hasattr(self, 'start_time') else 0,
            "hive_status": hive_status,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Continuous Hive Runner")
    parser.add_argument("--batch-size", type=int, default=3,
                       help="Number of surahs per batch (default: 3)")
    parser.add_argument("--interval", type=int, default=300,
                       help="Seconds between batches (default: 300 = 5 min)")
    parser.add_argument("--all-muqattaat", action="store_true",
                       help="Run all 29 surahs as single batch")
    
    args = parser.parse_args()
    
    runner = ContinuousHiveRunner(
        batch_size=args.batch_size,
        loop_interval=args.interval
    )
    
    if args.all_muqattaat:
        runner.batch_size = 29
    
    runner.run_continuous()


if __name__ == "__main__":
    main()
