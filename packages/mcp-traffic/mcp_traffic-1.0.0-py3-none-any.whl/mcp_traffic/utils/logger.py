"""
Logging utilities for MCP Traffic

Provides centralized logging configuration and utilities
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logger(name: str, 
                level: str = "INFO", 
                log_file: Optional[str] = None,
                console_output: bool = True) -> logging.Logger:
    """Set up a logger with file and console handlers
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        console_output: Whether to output to console
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_default_log_file(component: str) -> str:
    """Get default log file path for a component
    
    Args:
        component: Component name (e.g., 'collector', 'processor')
        
    Returns:
        Default log file path
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    return f"logs/{component}_{timestamp}.log"


def setup_application_logging(app_name: str = "mcp_traffic", 
                            level: str = "INFO") -> logging.Logger:
    """Set up application-wide logging
    
    Args:
        app_name: Application name
        level: Logging level
        
    Returns:
        Application logger
    """
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Set up main application logger
    main_log_file = get_default_log_file("application")
    logger = setup_logger(app_name, level, main_log_file)
    
    # Set up error logger
    error_log_file = "logs/error.log"
    error_logger = setup_logger(f"{app_name}.error", "ERROR", error_log_file, console_output=False)
    
    return logger


class LoggerMixin:
    """Mixin class to add logging capabilities to other classes"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        if not hasattr(self, '_logger'):
            class_name = self.__class__.__name__
            self._logger = logging.getLogger(f"mcp_traffic.{class_name}")
        return self._logger
        
    def setup_class_logger(self, level: str = "INFO", log_file: Optional[str] = None):
        """Set up logger specifically for this class
        
        Args:
            level: Logging level
            log_file: Optional log file path
        """
        class_name = self.__class__.__name__
        log_file = log_file or get_default_log_file(class_name.lower())
        self._logger = setup_logger(f"mcp_traffic.{class_name}", level, log_file)


def log_function_call(func):
    """Decorator to log function calls
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(f"mcp_traffic.{func.__module__}")
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {str(e)}")
            raise
            
    return wrapper


def log_execution_time(func):
    """Decorator to log function execution time
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    import time
    
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(f"mcp_traffic.{func.__module__}")
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {str(e)}")
            raise
            
    return wrapper


def configure_third_party_loggers(level: str = "WARNING"):
    """Configure third-party library loggers
    
    Args:
        level: Logging level for third-party loggers
    """
    # Reduce noise from urllib3
    logging.getLogger("urllib3.connectionpool").setLevel(getattr(logging, level.upper()))
    
    # Reduce noise from requests
    logging.getLogger("requests.packages.urllib3").setLevel(getattr(logging, level.upper()))
    
    # Other noisy libraries
    for logger_name in ["urllib3", "requests", "chardet"]:
        logging.getLogger(logger_name).setLevel(getattr(logging, level.upper()))


def get_log_files_info() -> dict:
    """Get information about existing log files
    
    Returns:
        Dictionary with log file information
    """
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return {"status": "no_logs_directory"}
    
    log_files = []
    for log_file in logs_dir.glob("*.log"):
        stat = log_file.stat()
        log_files.append({
            "name": log_file.name,
            "path": str(log_file),
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "lines": sum(1 for _ in open(log_file, 'r', encoding='utf-8', errors='ignore'))
        })
    
    return {
        "status": "found",
        "total_files": len(log_files),
        "total_size_mb": round(sum(f["size_mb"] for f in log_files), 2),
        "files": sorted(log_files, key=lambda x: x["modified"], reverse=True)
    }


def cleanup_old_logs(days: int = 30):
    """Clean up log files older than specified days
    
    Args:
        days: Number of days to keep logs
    """
    logger = logging.getLogger("mcp_traffic.log_cleanup")
    logs_dir = Path("logs")
    
    if not logs_dir.exists():
        return
    
    import time
    cutoff_time = time.time() - (days * 24 * 60 * 60)
    
    cleaned_files = []
    for log_file in logs_dir.glob("*.log"):
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
                cleaned_files.append(str(log_file))
            except Exception as e:
                logger.warning(f"Failed to delete {log_file}: {str(e)}")
    
    if cleaned_files:
        logger.info(f"Cleaned up {len(cleaned_files)} old log files")
    else:
        logger.debug("No old log files to clean up")


# Set up default logging configuration when module is imported
if not logging.getLogger().handlers:
    setup_application_logging()
    configure_third_party_loggers()
