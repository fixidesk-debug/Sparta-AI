"""
Logging configuration for the application
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        extra_fields = getattr(record, "extra_fields", None)
        if extra_fields:
            log_data.update(extra_fields)
        
        return json.dumps(log_data)


def setup_logging(log_level: str = "INFO", log_file: str = "logs/sparta_ai.log", enable_file_logging: bool = True):
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        enable_file_logging: Whether to enable file logging
    """
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # File handler with JSON formatting (only if enabled)
    if enable_file_logging:
        # Validate log file path to prevent path traversal
        # Only allow relative log_file paths and place them under the application's logs directory.
        base_dir = Path.cwd().resolve() / "logs"
        # Ensure base_dir is resolved
        base_dir = base_dir.resolve()
        # Reject absolute paths to prevent traversal outside the logs directory
        if Path(log_file).is_absolute():
            raise ValueError("log_file must be a relative path within the logs directory")
        # Build the target path under base_dir and resolve to eliminate ../ segments and symlinks
        log_path = (base_dir / log_file).resolve()
        # Ensure the resolved log_path is still inside base_dir
        try:
            log_path.relative_to(base_dir)
        except Exception:
            raise ValueError("Log file must be within logs directory")
        
        # Create logs directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            str(log_path),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)
    
    # Suppress noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    
    logging.info(f"Logging configured with level: {log_level}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)
