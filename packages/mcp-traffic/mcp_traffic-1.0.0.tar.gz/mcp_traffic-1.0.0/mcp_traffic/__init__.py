"""
MCP Traffic Package

Tokyo Traffic Data Collection System using ODPT API

This package provides tools for collecting, processing, and analyzing
Tokyo transportation data from the ODPT (Open Data Platform for Transportation) API.

Example usage:
    >>> from mcp_traffic import TrafficCollector, ConfigManager
    >>> config = ConfigManager('config/api_config.json')
    >>> collector = TrafficCollector(config)
    >>> data = collector.collect_train_data()
"""

__version__ = "1.0.0"
__author__ = "Tatsuru Kikuchi"
__email__ = "contact@mcp-traffic.example.com"
__description__ = "Tokyo traffic data collection and analysis system using ODPT API"
__url__ = "https://github.com/Tatsuru-Kikuchi/MCP-traffic"
__license__ = "MIT"

# Import main classes for convenience
try:
    from .collectors.traffic_collector import TrafficCollector
    from .utils.config import ConfigManager
    from .utils.api_client import ODPTClient
    from .utils.logger import setup_logger
except ImportError:
    # Handle case where dependencies aren't installed yet
    TrafficCollector = None
    ConfigManager = None
    ODPTClient = None
    setup_logger = None

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "__description__",
    "__url__",
    "__license__",
    "TrafficCollector",
    "ConfigManager", 
    "ODPTClient",
    "setup_logger"
]

def get_version():
    """Return the package version."""
    return __version__

def get_info():
    """Return package information."""
    return {
        "name": "mcp-traffic",
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "email": __email__,
        "url": __url__,
        "license": __license__
    }
