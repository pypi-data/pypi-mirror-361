import os
import sys
import platform
import logging
import tempfile
from pathlib import Path
from logging.handlers import RotatingFileHandler
import colorlog

def setup_logger(name: str = "MCPServerLogger", level: int = logging.INFO) -> logging.Logger:
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s: %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    try:
        # Platform-specific log directory
        if platform.system() == "Darwin":  # macOS
            try:
                log_dir = Path.home() / "Library" / "Logs" / "MCPKyvosServer"
            except:
                log_dir = Path.home() / "MCPKyvosServer" / "Logs"
        
        elif platform.system() == "Windows":
            appdata = os.getenv("APPDATA", str(Path.home() / "AppData" / "Roaming"))
            log_dir = Path(appdata) / "mcp_kyvos_server" / "Logs"

        else:  # Linux and others
            log_dir = Path.home() / ".mcp_kyvos_server" / "Logs"

        log_dir.mkdir(parents=True, exist_ok=True)
        log_filepath = log_dir / "mcp_kyvos_server_logs.log"

    except Exception as e:
        log_dir = Path(tempfile.gettempdir()) / "mcp_kyvos_server_logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_filepath = log_dir / "mcp_kyvos_server_logs.log"

    try:
        # Handlers
        file_handler = RotatingFileHandler(log_filepath, maxBytes=5 * 1024 * 1024, backupCount=3)
        stream_handler = logging.StreamHandler(sys.stderr)

        # Formatters
        color_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)s - %(module)s: %(message)s",
            datefmt=DATE_FORMAT,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
                "EXCEPTION": "red",
                "CRITICAL": "bold_red",
            },
        )

        file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

        logger = logging.getLogger(name)
        logger.setLevel(level)

        if not logger.handlers:  # Prevent duplicate handlers
            file_handler.setFormatter(file_formatter)
            stream_handler.setFormatter(color_formatter)

            logger.addHandler(file_handler)
            logger.addHandler(stream_handler)

        logger.propagate = False

    except Exception as e:
        print(f"[Logger Error] Failed to initialize handlers: {e}")

    return logger, log_filepath