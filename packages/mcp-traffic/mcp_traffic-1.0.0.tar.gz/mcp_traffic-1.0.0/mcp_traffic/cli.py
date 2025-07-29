#!/usr/bin/env python3
"""
MCP Traffic Command Line Interface

Provides command-line access to MCP Traffic functionality
"""

import sys
import argparse
import json
from typing import Optional
from pathlib import Path

try:
    from .collectors.traffic_collector import TrafficCollector
    from .utils.config import ConfigManager
    from .utils.logger import setup_logger
    from . import __version__, get_info
except ImportError:
    # Fallback for development
    sys.path.append(str(Path(__file__).parent))
    from collectors.traffic_collector import TrafficCollector
    from utils.config import ConfigManager
    from utils.logger import setup_logger
    __version__ = "1.0.0"
    def get_info():
        return {"name": "mcp-traffic", "version": __version__}


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        prog="mcp-traffic",
        description="MCP Traffic - Tokyo Traffic Data Collection System",
        epilog="For more information, visit: https://github.com/Tatsuru-Kikuchi/MCP-traffic"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"mcp-traffic {__version__}"
    )
    
    parser.add_argument(
        "--config", 
        default="config/api_config.json",
        help="Path to configuration file (default: config/api_config.json)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Collect command
    collect_parser = subparsers.add_parser(
        "collect", 
        help="Collect traffic data"
    )
    collect_parser.add_argument(
        "--type",
        choices=["all", "catalog", "train", "bus"],
        default="all",
        help="Type of data to collect (default: all)"
    )
    collect_parser.add_argument(
        "--operator",
        help="Filter by specific operator"
    )
    collect_parser.add_argument(
        "--output",
        help="Output file path (optional)"
    )
    
    # Status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show system status and information"
    )
    status_parser.add_argument(
        "--format",
        choices=["json", "table"],
        default="table",
        help="Output format (default: table)"
    )
    
    # Test command
    test_parser = subparsers.add_parser(
        "test",
        help="Test API connectivity and configuration"
    )
    
    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Show package information"
    )
    
    return parser


def handle_collect_command(args, collector: TrafficCollector):
    """Handle collect command"""
    logger = setup_logger("mcp_traffic.cli", args.log_level)
    
    try:
        if args.type == "all":
            logger.info("Collecting all data types")
            data = collector.collect_all_data()
        elif args.type == "catalog":
            logger.info("Collecting catalog data")
            data = collector.collect_catalog()
        elif args.type == "train":
            logger.info("Collecting train data")
            data = collector.collect_train_data()
        elif args.type == "bus":
            logger.info("Collecting bus data")
            data = collector.collect_bus_data()
        
        # Save to custom output file if specified
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Data saved to {output_path}")
        
        print("✅ Data collection completed successfully")
        
    except Exception as e:
        logger.error(f"Data collection failed: {str(e)}")
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def handle_status_command(args, collector: TrafficCollector):
    """Handle status command"""
    logger = setup_logger("mcp_traffic.cli", args.log_level)
    
    try:
        # Get data summary
        data_summary = collector.get_data_summary()
        
        # Get API health
        api_health = collector.api_client.get_health_status()
        
        # Get package info
        pkg_info = get_info()
        
        status_info = {
            "package": pkg_info,
            "api_health": api_health,
            "data_summary": data_summary,
            "config_path": str(collector.config_manager.config_path)
        }
        
        if args.format == "json":
            print(json.dumps(status_info, indent=2))
        else:
            # Table format
            print("🚇 MCP Traffic System Status")
            print("=" * 50)
            print(f"📦 Package: {pkg_info['name']} v{pkg_info['version']}")
            print(f"🔧 Config: {collector.config_manager.config_path}")
            print()
            
            print("🌐 API Status:")
            if api_health['status'] == 'healthy':
                print(f"   ✅ Status: {api_health['status']}")
                print(f"   ⏱️  Response Time: {api_health['response_time_seconds']}s")
                print(f"   📊 Catalog Items: {api_health.get('catalog_items', 'N/A')}")
            else:
                print(f"   ❌ Status: {api_health['status']}")
                print(f"   ⏱️  Response Time: {api_health['response_time_seconds']}s")
                print(f"   ❗ Error: {api_health.get('error', 'Unknown')}")
            print()
            
            print("📁 Data Files:")
            print(f"   📄 Raw Files: {data_summary['raw_files']}")
            print(f"   🔄 Processed Files: {data_summary['processed_files']}")
            print(f"   📚 Archived Files: {data_summary['archived_files']}")
            
            if data_summary.get('latest_collection'):
                latest = data_summary['latest_collection']
                print(f"   🕐 Latest Collection: {latest['timestamp']}")
                print(f"   💾 File Size: {latest['size_mb']} MB")
        
    except Exception as e:
        logger.error(f"Failed to get status: {str(e)}")
        print(f"❌ Error getting status: {str(e)}", file=sys.stderr)
        sys.exit(1)


def handle_test_command(args, collector: TrafficCollector):
    """Handle test command"""
    logger = setup_logger("mcp_traffic.cli", args.log_level)
    
    print("🧪 Testing MCP Traffic System")
    print("=" * 40)
    
    # Test configuration
    print("📋 Testing configuration...")
    try:
        config = collector.config_manager.get_config()
        print("   ✅ Configuration loaded successfully")
    except Exception as e:
        print(f"   ❌ Configuration error: {str(e)}")
        sys.exit(1)
    
    # Test API connection
    print("🌐 Testing API connection...")
    try:
        if collector.api_client.test_connection():
            print("   ✅ API connection successful")
        else:
            print("   ❌ API connection failed")
            sys.exit(1)
    except Exception as e:
        print(f"   ❌ API connection error: {str(e)}")
        sys.exit(1)
    
    # Test data collection
    print("📊 Testing data collection...")
    try:
        catalog = collector.collect_catalog()
        if catalog:
            print("   ✅ Data collection test successful")
            print(f"   📈 Retrieved {len(catalog) if isinstance(catalog, list) else 1} catalog items")
        else:
            print("   ⚠️  Data collection returned empty results")
    except Exception as e:
        print(f"   ❌ Data collection error: {str(e)}")
        sys.exit(1)
    
    print("\n🎉 All tests passed! System is ready to use.")


def handle_info_command(args):
    """Handle info command"""
    info = get_info()
    
    print("🚇 MCP Traffic Package Information")
    print("=" * 40)
    print(f"📦 Name: {info['name']}")
    print(f"🏷️  Version: {info['version']}")
    print(f"📝 Description: {info.get('description', 'Tokyo traffic data collection system')}")
    print(f"👤 Author: {info.get('author', 'Tatsuru Kikuchi')}")
    print(f"🌐 URL: {info.get('url', 'https://github.com/Tatsuru-Kikuchi/MCP-traffic')}")
    print(f"📄 License: {info.get('license', 'MIT')}")


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle commands that don't need collector
    if args.command == "info":
        handle_info_command(args)
        return
    
    # Initialize collector for other commands
    try:
        collector = TrafficCollector(args.config)
    except Exception as e:
        print(f"❌ Failed to initialize collector: {str(e)}", file=sys.stderr)
        print(f"💡 Check your configuration file: {args.config}")
        sys.exit(1)
    
    # Handle commands
    if args.command == "collect":
        handle_collect_command(args, collector)
    elif args.command == "status":
        handle_status_command(args, collector)
    elif args.command == "test":
        handle_test_command(args, collector)


if __name__ == "__main__":
    main()
