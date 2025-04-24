import sys
from pathlib import Path

from app.helpers.utilities.envVar import envConfig

# Define the log directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "json": {"format": '{ "time":"%(asctime)s", "name":"%(name)s", "level":"%(levelname)s", "message":"%(message)s", "module":"%(module)s" }'},
        "access": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": sys.stdout,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": LOG_DIR / "app.log",
            "maxBytes": 1024 * 1024 * 10,  # 1 MB
            "backupCount": 5,
        },
        "access_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "access",
            "filename": LOG_DIR / "access.log",
            "maxBytes": 1024 * 1024,  # 1 MB
            "backupCount": 5,
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": LOG_DIR / "error.log",
            "maxBytes": 1024 * 1024,  # 1 MB
            "backupCount": 5,
            "level": "ERROR",
        },
        "json_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": LOG_DIR / "json.log",
            "maxBytes": 1024 * 1024,  # 1 MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["console"] if envConfig.app_reload else ["console", "file"],
            "level": "DEBUG" if envConfig.debug_logs_enabled else ["INFO"],
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["console"] if envConfig.app_reload else ["console", "file", "error_file"],
            "level": "ERROR",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"] if envConfig.app_reload else ["console", "access_file", "error_file"],
            "level": "DEBUG" if envConfig.debug_logs_enabled else ["INFO"],
            "propagate": False,
        },
        "fastapi": {
            "handlers": ["console"] if envConfig.app_reload else ["console", "file", "json_file"],
            "level": "DEBUG" if envConfig.debug_logs_enabled else ["INFO"],
            "propagate": False,
        },
        "app": {
            "handlers": ["console"] if envConfig.app_reload else ["console", "file", "json_file"],
            "level": "DEBUG" if envConfig.debug_logs_enabled else ["INFO"],
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"] if envConfig.app_reload else ["console", "file", "json_file"],
        "level": "DEBUG" if envConfig.debug_logs_enabled else ["INFO"],
    },
}
