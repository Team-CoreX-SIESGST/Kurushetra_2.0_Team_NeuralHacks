"""
Enhanced logging configuration for OmniSearch AI.
Provides structured logging with multiple handlers and formatters.
"""

import logging
import logging.handlers
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import sys
import traceback

# Create logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
            
        return json.dumps(log_entry, ensure_ascii=False)

class ColoredFormatter(logging.Formatter):
    """Colored console formatter for better readability."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'ENDC': '\033[0m',      # End color
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        reset_color = self.COLORS['ENDC']
        
        # Format the message
        formatted_message = super().format(record)
        return f"{log_color}{formatted_message}{reset_color}"

def setup_logging(
    level: str = "INFO",
    enable_file_logging: bool = True,
    enable_json_logging: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup comprehensive logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_file_logging: Enable file logging
        enable_json_logging: Enable structured JSON logging
        max_file_size: Maximum size of log files before rotation
        backup_count: Number of backup files to keep
    
    Returns:
        Configured logger instance
    """
    
    # Get root logger
    logger = logging.getLogger("omnisearch")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)-8s | %(name)-15s | %(funcName)-20s:%(lineno)-3d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    if enable_file_logging:
        # Application log file (rotating)
        app_handler = logging.handlers.RotatingFileHandler(
            LOGS_DIR / "omnisearch.log",
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        app_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-15s | %(funcName)-20s:%(lineno)-3d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        app_handler.setFormatter(app_formatter)
        logger.addHandler(app_handler)
        
        # Error log file (errors only)
        error_handler = logging.handlers.RotatingFileHandler(
            LOGS_DIR / "omnisearch_errors.log",
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(app_formatter)
        logger.addHandler(error_handler)
        
        if enable_json_logging:
            # JSON structured logging
            json_handler = logging.handlers.RotatingFileHandler(
                LOGS_DIR / "omnisearch.json.log",
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            json_handler.setFormatter(JSONFormatter())
            logger.addHandler(json_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(f"omnisearch.{name}")

def log_exception(logger: logging.Logger, exc: Exception, extra_data: Optional[Dict[str, Any]] = None):
    """Log an exception with additional context."""
    logger.error(
        f"Exception occurred: {type(exc).__name__}: {str(exc)}",
        exc_info=True,
        extra={'extra_data': extra_data or {}}
    )

def log_api_call(
    logger: logging.Logger,
    method: str,
    endpoint: str,
    user_id: str,
    duration: float,
    status_code: int,
    extra_data: Optional[Dict[str, Any]] = None
):
    """Log API call with metrics."""
    logger.info(
        f"API {method} {endpoint} | User: {user_id} | {status_code} | {duration:.3f}s",
        extra={
            'extra_data': {
                'method': method,
                'endpoint': endpoint,
                'user_id': user_id,
                'duration_seconds': duration,
                'status_code': status_code,
                'type': 'api_call',
                **(extra_data or {})
            }
        }
    )

def log_ai_operation(
    logger: logging.Logger,
    operation: str,
    model: str,
    duration: float,
    token_count: Optional[int] = None,
    success: bool = True,
    extra_data: Optional[Dict[str, Any]] = None
):
    """Log AI operation with metrics."""
    logger.info(
        f"AI Operation: {operation} | Model: {model} | {duration:.3f}s | {'Success' if success else 'Failed'}",
        extra={
            'extra_data': {
                'operation': operation,
                'model': model,
                'duration_seconds': duration,
                'token_count': token_count,
                'success': success,
                'type': 'ai_operation',
                **(extra_data or {})
            }
        }
    )

def log_file_operation(
    logger: logging.Logger,
    operation: str,
    file_id: str,
    filename: str,
    file_size: int,
    duration: float,
    success: bool = True,
    extra_data: Optional[Dict[str, Any]] = None
):
    """Log file operation with metrics."""
    logger.info(
        f"File {operation}: {filename} ({file_id}) | {file_size} bytes | {duration:.3f}s | {'Success' if success else 'Failed'}",
        extra={
            'extra_data': {
                'operation': operation,
                'file_id': file_id,
                'filename': filename,
                'file_size': file_size,
                'duration_seconds': duration,
                'success': success,
                'type': 'file_operation',
                **(extra_data or {})
            }
        }
    )

# Initialize logging on module import
setup_logging()
