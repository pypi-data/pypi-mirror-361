#!/usr/bin/env python3
"""
MCP Traffic - Collect All Data Script

This script runs a comprehensive data collection from the ODPT API
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from collectors.traffic_collector import TrafficCollector
from utils.logger import setup_logger


def main():
    """Main function to run data collection"""
    parser = argparse.ArgumentParser(description="MCP Traffic - Collect All Data")
    parser.add_argument("--config", default="config/api_config.json",
                       help="Path to configuration file")
    parser.add_argument("--dry-run", action="store_true",
                       help="Run without actually collecting data")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--output-summary", action="store_true",
                       help="Output collection summary at the end")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logger(__name__, level=log_level)
    
    logger.info("=== MCP Traffic Data Collection Started ===")
    logger.info(f"Configuration file: {args.config}")
    logger.info(f"Dry run mode: {args.dry_run}")
    
    try:
        # Check if config file exists
        config_path = Path(args.config)
        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            logger.info("Please copy config/api_config.example.json to config/api_config.json and configure it")
            return 1
        
        if args.dry_run:
            logger.info("DRY RUN MODE - No data will be collected")
            
            # Test configuration loading
            try:
                collector = TrafficCollector(args.config)
                logger.info("✓ Configuration loaded successfully")
                
                # Test API connectivity
                test_result = collector.api_client.test_connection()
                if test_result:
                    logger.info("✓ API connection test successful")
                else:
                    logger.warning("⚠ API connection test failed")
                    
                # Show what would be collected
                logger.info("Would collect the following data types:")
                data_types = collector.config_manager.get_data_types()
                for data_type in data_types:
                    logger.info(f"  - {data_type}")
                    
            except Exception as e:
                logger.error(f"✗ Dry run failed: {str(e)}")
                return 1
                
            logger.info("Dry run completed successfully")
            return 0
        
        # Initialize collector
        collector = TrafficCollector(args.config)
        
        # Test API connection first
        logger.info("Testing API connection...")
        if not collector.api_client.test_connection():
            logger.error("API connection test failed. Please check your configuration.")
            return 1
        
        logger.info("API connection successful. Starting data collection...")
        
        # Collect all data
        start_time = datetime.now()
        collected_data = collector.collect_all_data()
        end_time = datetime.now()
        
        duration = end_time - start_time
        logger.info(f"Data collection completed in {duration.total_seconds():.2f} seconds")
        
        # Output summary if requested
        if args.output_summary:
            summary = collector.get_data_summary()
            print("\n=== Collection Summary ===")
            print(json.dumps(summary, indent=2))
            
        logger.info("=== MCP Traffic Data Collection Completed Successfully ===")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Data collection interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Data collection failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
