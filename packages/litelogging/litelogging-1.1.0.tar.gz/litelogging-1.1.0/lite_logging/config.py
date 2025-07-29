from lite_logging.log_colors import LogColors

LOGGING_ENABLED = True
DEBUG_MODE = True
LOG_LEVEL = {
    "INFO": {
        "color": LogColors.OKGREEN,
        "enabled": True
    },
    "DEBUG": {
        "color": LogColors.OKCYAN,
        "enabled": DEBUG_MODE
    },
    "WARNING": {
        "color": LogColors.WARNING,
        "enabled": True
    },
    "ERROR": {
        "color": LogColors.FAIL,
        "enabled": True
    },
    "CRITICAL": {
        "color": LogColors.OKMAGENTA,
        "enabled": True
    }
}