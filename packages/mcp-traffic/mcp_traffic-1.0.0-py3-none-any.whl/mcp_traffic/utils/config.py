"""
Configuration Management for MCP Traffic

Handles loading and validation of configuration files
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class ConfigManager:
    """Configuration manager for MCP Traffic system"""
    
    def __init__(self, config_path: str = "config/api_config.json"):
        """Initialize configuration manager
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file
        
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in config file {self.config_path}: {str(e)}")
            
    def _validate_config(self) -> None:
        """Validate configuration structure and required fields
        
        Raises:
            ValueError: If required configuration fields are missing
        """
        required_sections = ["odpt_api", "collection", "storage"]
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
                
        # Validate ODPT API configuration
        odpt_config = self.config.get("odpt_api", {})
        required_odpt_fields = ["base_url", "api_key"]
        
        for field in required_odpt_fields:
            if field not in odpt_config:
                raise ValueError(f"Missing required ODPT API field: {field}")
                
        # Check if API key is placeholder
        if odpt_config["api_key"] == "YOUR_API_KEY_HERE":
            logging.warning("API key appears to be placeholder. Please configure with actual API key.")
            
    def get_config(self) -> Dict[str, Any]:
        """Get the complete configuration
        
        Returns:
            Configuration dictionary
        """
        return self.config
        
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get a specific configuration section
        
        Args:
            section: Section name to retrieve
            
        Returns:
            Section configuration dictionary
            
        Raises:
            KeyError: If section doesn't exist
        """
        if section not in self.config:
            raise KeyError(f"Configuration section '{section}' not found")
        return self.config[section]
        
    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """Get a specific configuration value
        
        Args:
            section: Section name
            key: Key within the section
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        section_config = self.config.get(section, {})
        return section_config.get(key, default)
        
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values
        
        Args:
            updates: Dictionary of updates to apply
        """
        def update_nested(d: dict, u: dict) -> dict:
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = update_nested(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
            
        self.config = update_nested(self.config, updates)
        self._validate_config()
        
    def save_config(self, path: Optional[str] = None) -> None:
        """Save current configuration to file
        
        Args:
            path: Optional path to save to (defaults to original path)
        """
        save_path = Path(path) if path else self.config_path
        
        # Create directory if it doesn't exist
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
            
    def get_api_url(self, endpoint: str = "") -> str:
        """Get full API URL for a given endpoint
        
        Args:
            endpoint: API endpoint to append
            
        Returns:
            Full API URL
        """
        base_url = self.get_value("odpt_api", "base_url")
        return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}" if endpoint else base_url
        
    def get_api_key(self) -> str:
        """Get API key
        
        Returns:
            API key string
        """
        return self.get_value("odpt_api", "api_key")
        
    def get_rate_limit(self) -> int:
        """Get API rate limit
        
        Returns:
            Rate limit in requests per minute
        """
        return self.get_value("odpt_api", "rate_limit", 100)
        
    def get_timeout(self) -> int:
        """Get request timeout
        
        Returns:
            Timeout in seconds
        """
        return self.get_value("odpt_api", "timeout", 30)
        
    def get_data_types(self) -> list:
        """Get configured data types to collect
        
        Returns:
            List of data types
        """
        return self.get_value("collection", "data_types", ["train", "bus", "station"])
        
    def is_real_time_enabled(self) -> bool:
        """Check if real-time collection is enabled
        
        Returns:
            True if real-time collection is enabled
        """
        return self.get_value("collection", "enable_real_time", True)
        
    def get_storage_format(self) -> str:
        """Get storage format
        
        Returns:
            Storage format (json, csv, etc.)
        """
        return self.get_value("storage", "format", "json")
        
    def is_compression_enabled(self) -> bool:
        """Check if compression is enabled
        
        Returns:
            True if compression is enabled
        """
        return self.get_value("storage", "compression", True)
        
    def get_retention_days(self) -> int:
        """Get data retention period in days
        
        Returns:
            Retention period in days
        """
        return self.get_value("storage", "retention_days", 365)
        
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"ConfigManager(path={self.config_path}, sections={list(self.config.keys())})"
        
    def __repr__(self) -> str:
        """Detailed string representation"""
        return self.__str__()
