#!/usr/bin/env python3
"""
MCP Traffic - Scheduled Collection Script

This script runs continuous scheduled data collection from the ODPT API
"""

import sys
import os
import time
import signal
import threading
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from collectors.traffic_collector import TrafficCollector
from utils.logger import setup_logger
from utils.config import ConfigManager


class ScheduledCollector:
    """Handles scheduled data collection"""
    
    def __init__(self, config_path: str = "config/api_config.json"):
        """Initialize scheduled collector
        
        Args:
            config_path: Path to configuration file
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        self.logger = setup_logger(__name__)
        self.collector = TrafficCollector(config_path)
        
        # Scheduling configuration
        self.schedule_interval = self.config_manager.get_value("collection", "schedule_interval", 300)  # 5 minutes default
        self.is_running = False
        self.collection_thread = None
        
        # Statistics
        self.stats = {
            "start_time": None,
            "total_collections": 0,
            "successful_collections": 0,
            "failed_collections": 0,
            "last_collection_time": None,
            "last_error": None
        }
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        
    def _collection_loop(self):
        """Main collection loop"""
        self.logger.info(f"Starting scheduled collection every {self.schedule_interval} seconds")
        
        while self.is_running:
            try:
                collection_start = datetime.now()
                self.logger.info("Starting scheduled data collection...")
                
                # Perform data collection
                collected_data = self.collector.collect_all_data()
                
                collection_end = datetime.now()
                duration = (collection_end - collection_start).total_seconds()
                
                # Update statistics
                self.stats["total_collections"] += 1
                self.stats["successful_collections"] += 1
                self.stats["last_collection_time"] = collection_end.isoformat()
                
                self.logger.info(f"Collection completed successfully in {duration:.2f} seconds")
                
                # Log collection summary
                if collected_data:
                    train_count = len(collected_data.get("train_data", {}).get("odpt:Train", []))
                    bus_count = len(collected_data.get("bus_data", {}).get("odpt:Bus", []))
                    self.logger.info(f"Collected {train_count} train records, {bus_count} bus records")
                
            except Exception as e:
                self.stats["total_collections"] += 1
                self.stats["failed_collections"] += 1
                self.stats["last_error"] = str(e)
                self.logger.error(f"Collection failed: {str(e)}")
                
            # Wait for next collection (if still running)
            if self.is_running:
                self.logger.debug(f"Waiting {self.schedule_interval} seconds until next collection...")
                
                # Use shorter sleep intervals to allow for responsive shutdown
                sleep_remaining = self.schedule_interval
                while sleep_remaining > 0 and self.is_running:
                    sleep_time = min(1, sleep_remaining)  # Sleep in 1-second intervals
                    time.sleep(sleep_time)
                    sleep_remaining -= sleep_time
                    
    def start(self):
        """Start scheduled collection"""
        if self.is_running:
            self.logger.warning("Scheduled collection is already running")
            return
            
        self.logger.info("Starting MCP Traffic scheduled collection service")
        
        # Test API connection first
        if not self.collector.api_client.test_connection():
            raise RuntimeError("API connection test failed. Please check your configuration.")
            
        self.is_running = True
        self.stats["start_time"] = datetime.now().isoformat()
        
        # Start collection thread
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        
        self.logger.info("Scheduled collection service started successfully")
        
    def stop(self):
        """Stop scheduled collection"""
        if not self.is_running:
            return
            
        self.logger.info("Stopping scheduled collection service...")
        self.is_running = False
        
        # Wait for collection thread to finish
        if self.collection_thread and self.collection_thread.is_alive():
            self.collection_thread.join(timeout=30)  # Wait up to 30 seconds
            
        self.logger.info("Scheduled collection service stopped")
        
    def get_status(self) -> dict:
        """Get current status of the scheduled collector
        
        Returns:
            Status dictionary
        """
        status = {
            "is_running": self.is_running,
            "schedule_interval_seconds": self.schedule_interval,
            "uptime_seconds": None,
            "next_collection_in_seconds": None,
            "statistics": self.stats.copy()
        }
        
        if self.stats["start_time"]:
            start_time = datetime.fromisoformat(self.stats["start_time"])
            uptime = datetime.now() - start_time
            status["uptime_seconds"] = int(uptime.total_seconds())
            
        if self.stats["last_collection_time"]:
            last_collection = datetime.fromisoformat(self.stats["last_collection_time"])
            next_collection = last_collection + timedelta(seconds=self.schedule_interval)
            time_until_next = next_collection - datetime.now()
            
            if time_until_next.total_seconds() > 0:
                status["next_collection_in_seconds"] = int(time_until_next.total_seconds())
            else:
                status["next_collection_in_seconds"] = 0
                
        return status
        
    def run_forever(self):
        """Run the scheduled collector indefinitely"""
        try:
            self.start()
            
            # Keep the main thread alive
            while self.is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
        finally:
            self.stop()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Traffic - Scheduled Collection Service")
    parser.add_argument("--config", default="config/api_config.json",
                       help="Path to configuration file")
    parser.add_argument("--interval", type=int,
                       help="Collection interval in seconds (overrides config)")
    parser.add_argument("--once", action="store_true",
                       help="Run collection once and exit")
    parser.add_argument("--status", action="store_true",
                       help="Show status and exit")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    try:
        # Check if config file exists
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Configuration file not found: {config_path}")
            print("Please copy config/api_config.example.json to config/api_config.json and configure it")
            return 1
            
        # Initialize scheduled collector
        scheduled_collector = ScheduledCollector(args.config)
        
        # Override interval if specified
        if args.interval:
            scheduled_collector.schedule_interval = args.interval
            scheduled_collector.logger.info(f"Using custom interval: {args.interval} seconds")
            
        # Set verbose logging if requested
        if args.verbose:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
            
        if args.status:
            # Show status
            status = scheduled_collector.get_status()
            import json
            print(json.dumps(status, indent=2))
            return 0
            
        elif args.once:
            # Run once and exit
            scheduled_collector.logger.info("Running single collection...")
            collector = TrafficCollector(args.config)
            collector.collect_all_data()
            scheduled_collector.logger.info("Single collection completed")
            return 0
            
        else:
            # Run scheduled collection
            scheduled_collector.logger.info("Starting MCP Traffic scheduled collection service")
            scheduled_collector.run_forever()
            return 0
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
