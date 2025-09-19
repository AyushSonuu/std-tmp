# app/core/logging.py
import sys
from loguru import logger

def setup_logging():
    """
    Configures the Loguru logger for the application.
    - Removes default handlers.
    - Adds a human-readable handler for development (stderr).
    - Adds a file handler for structured JSON logging in production.
    """
    logger.remove()  # Remove default handler to avoid duplicate logs

    # Development-friendly logger
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # Production-ready file logger (structured JSON)
    logger.add(
        "logs/app.log",
        level="INFO",
        format="{message}",  # The JSON formatter will handle the structure
        serialize=True,      # This is the key for JSON logging
        rotation="10 MB",    # Rotate the log file when it reaches 10 MB
        compression="zip",   # Compress old log files
        enqueue=True,        # Make logging non-blocking
        catch=True,          # Catch exceptions from logger sinks
    )

    logger.info("Logger configured successfully.")