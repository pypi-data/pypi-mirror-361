from datetime import datetime

_LEVELS = {
    "ERROR":     0,
    "WARN":      1,
    "INFO":      2,
    "DEBUG":     3,
    "DEV DEBUG": 4,
    "OFF":      99,
}

_current = _LEVELS["OFF"]  # Standard: alles aus

def set_debug_mode(active=True):
    global _current
    _current = _LEVELS["DEV DEBUG"] if active else _LEVELS["OFF"]

def _log(level, msg):
    level_value = _LEVELS.get(level, _LEVELS["OFF"])
    if _current <= _LEVELS["OFF"]:  # alles deaktiviert
        return
    if level_value <= _current:
        ts = datetime.now().strftime("%H:%MUhr %d.%m.%Y")
        print(f"[{level}] {ts} = {msg}")

def error(m):     _log("ERROR", m)
def warn(m):      _log("WARN", m)
def info(m):      _log("INFO", m)
def debug(m):     _log("DEBUG", m)
def dev_debug(m): _log("DEV DEBUG", m)
