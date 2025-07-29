#!/usr/bin/env python3
"""
MCP Traffic Collector - Main data collection module for ODPT API

This module handles the collection of traffic data from the ODPT 
(Open Data Platform for Transportation) API for Tokyo transportation systems.
"""

import json
import os
import sys
import time
import logging
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import requests
from pathlib import Path

try:
    from ..utils.config import ConfigManager
    from ..utils.logger import setup_logger
    from ..utils.api_client import ODPTClient
except ImportError:
    # Fallback for development/testing
    sys.path.append(str(Path(__file__).parent.parent))
    from utils.config import ConfigManager
    from utils.logger import setup_logger
    from utils.api_client import ODPTClient


class TrafficCollector:
    """Main traffic data collector class"""
    
    def __init__(self, config_path: str = "config/api_config.json"):
        """Initialize the traffic collector
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        self.logger = setup_logger(__name__)
        self.api_client = ODPTClient(self.config)
        
        # Create data directories
        self._create_directories()
        
    def _create_directories(self) -> None:
        """Create necessary data directories"""
        directories = [
            "data/raw",
            "data/processed", 
            "data/archives",
            "logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
    def collect_catalog(self) -> Dict[str, Any]:
        """Collect API catalog information
        
        Returns:
            Dict containing catalog data
        """
        self.logger.info("Collecting ODPT API catalog")
        
        try:
            catalog_data = self.api_client.get_catalog()
            
            # Save catalog data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            catalog_file = f"data/raw/catalog_{timestamp}.json"
            
            with open(catalog_file, 'w', encoding='utf-8') as f:
                json.dump(catalog_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Catalog saved to {catalog_file}")
            return catalog_data
            
        except Exception as e:
            self.logger.error(f"Failed to collect catalog: {str(e)}")
            raise
            
    def collect_train_data(self) -> Dict[str, Any]:
        """Collect train information data
        
        Returns:
            Dict containing train data
        """
        self.logger.info("Collecting train data")
        
        try:
            # Collect various train-related data
            data_types = [
                "odpt:Train",
                "odpt:TrainInformation", 
                "odpt:Railway",
                "odpt:Station"
            ]
            
            collected_data = {}
            
            for data_type in data_types:
                self.logger.info(f"Collecting {data_type}")
                data = self.api_client.get_data(data_type)
                collected_data[data_type] = data
                
                # Add small delay to respect rate limits
                time.sleep(0.1)
                
            # Save data with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data_file = f"data/raw/train_data_{timestamp}.json"
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(collected_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Train data saved to {data_file}")
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Failed to collect train data: {str(e)}")
            raise
            
    def collect_bus_data(self) -> Dict[str, Any]:
        """Collect bus information data
        
        Returns:
            Dict containing bus data
        """
        self.logger.info("Collecting bus data")
        
        try:
            # Collect bus-related data
            data_types = [
                "odpt:Bus",
                "odpt:BusroutePattern",
                "odpt:BusstopPole"
            ]
            
            collected_data = {}
            
            for data_type in data_types:
                self.logger.info(f"Collecting {data_type}")
                data = self.api_client.get_data(data_type)
                collected_data[data_type] = data
                
                # Add small delay to respect rate limits
                time.sleep(0.1)
                
            # Save data with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data_file = f"data/raw/bus_data_{timestamp}.json"
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(collected_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Bus data saved to {data_file}")
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Failed to collect bus data: {str(e)}")
            raise
            
    def collect_all_data(self) -> Dict[str, Any]:
        """Collect all available traffic data
        
        Returns:
            Dict containing all collected data
        """
        self.logger.info("Starting comprehensive data collection")
        
        all_data = {
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "catalog": None,
            "train_data": None,
            "bus_data": None
        }
        
        try:
            # Collect catalog first
            all_data["catalog"] = self.collect_catalog()
            
            # Collect train data
            all_data["train_data"] = self.collect_train_data()
            
            # Collect bus data  
            all_data["bus_data"] = self.collect_bus_data()
            
            # Save comprehensive data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            comprehensive_file = f"data/raw/comprehensive_data_{timestamp}.json"
            
            with open(comprehensive_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Comprehensive data saved to {comprehensive_file}")
            self.logger.info("Data collection completed successfully")
            
            return all_data
            
        except Exception as e:
            self.logger.error(f"Failed to collect all data: {str(e)}")
            raise
            
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of collected data
        
        Returns:
            Dict containing data summary statistics
        """
        raw_dir = Path("data/raw")
        processed_dir = Path("data/processed")
        archives_dir = Path("data/archives")
        
        summary = {
            "raw_files": len(list(raw_dir.glob("*.json"))) if raw_dir.exists() else 0,
            "processed_files": len(list(processed_dir.glob("*.json"))) if processed_dir.exists() else 0,
            "archived_files": len(list(archives_dir.glob("*.json"))) if archives_dir.exists() else 0,
            "latest_collection": None
        }
        
        # Find latest collection file
        if raw_dir.exists():
            json_files = list(raw_dir.glob("*.json"))
            if json_files:
                latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
                summary["latest_collection"] = {
                    "file": str(latest_file),
                    "timestamp": datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat(),
                    "size_mb": round(latest_file.stat().st_size / (1024 * 1024), 2)
                }
                
        return summary


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="MCP Traffic Data Collector")
    parser.add_argument("--catalog-only", action="store_true", 
                       help="Collect only catalog information")
    parser.add_argument("--train-only", action="store_true",
                       help="Collect only train data") 
    parser.add_argument("--bus-only", action="store_true",
                       help="Collect only bus data")
    parser.add_argument("--summary", action="store_true",
                       help="Show data collection summary")
    parser.add_argument("--config", default="config/api_config.json",
                       help="Path to configuration file")
    
    args = parser.parse_args()
    
    try:
        collector = TrafficCollector(args.config)
        
        if args.summary:
            summary = collector.get_data_summary()
            print(json.dumps(summary, indent=2))
            return
            
        if args.catalog_only:
            collector.collect_catalog()
        elif args.train_only:
            collector.collect_train_data()
        elif args.bus_only:
            collector.collect_bus_data()
        else:
            collector.collect_all_data()
            
        print("Data collection completed successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
