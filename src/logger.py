"""Loguru logger configuration"""

import os
from loguru import logger
import sys

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Remove default logger
logger.remove()

# Add console handler with nice formatting
logger.add(
    sys.stderr,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    level="INFO",
    colorize=True,
)

# Add file handler for all logs
logger.add(
    os.path.join(LOGS_DIR, "app.log"),
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    level="DEBUG",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
        "{name}:{function}:{line} - {message}"
    ),
)

# Add file handler for errors only
logger.add(
    os.path.join(LOGS_DIR, "errors.log"),
    rotation="10 MB",
    retention="90 days",
    compression="zip",
    level="ERROR",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
        "{name}:{function}:{line} - {message}\n{exception}"
    ),
    backtrace=True,
    diagnose=True,
)

__all__ = ["logger"]
