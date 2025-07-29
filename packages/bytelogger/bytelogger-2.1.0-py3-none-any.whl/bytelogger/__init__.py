from .better_logger import debug, dev_debug, info, warn, error, set_debug_mode
from .get_logs import start_logging

__all__ = ["init", "debug", "dev_debug", "info", "warn", "error"]

def init(debug_mode=True, log_mode=True):
    if debug_mode:
        set_debug_mode(True)
    if log_mode:
        start_logging()

init(debug_mode=True, log_mode=True)
