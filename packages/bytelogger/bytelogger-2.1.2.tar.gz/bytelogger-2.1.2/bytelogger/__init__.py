from .better_logger import debug, dev_debug, info, warn, error, set_debug_mode
from .get_logs import start_logging

__all__ = ["init", "debug", "dev_debug", "info", "warn", "error"]

_has_logging_started = False

def init(debug_mode=True, log_mode=True):
    global _has_logging_started
    set_debug_mode(debug_mode)
    if log_mode and not _has_logging_started:
        start_logging()
        _has_logging_started = True
