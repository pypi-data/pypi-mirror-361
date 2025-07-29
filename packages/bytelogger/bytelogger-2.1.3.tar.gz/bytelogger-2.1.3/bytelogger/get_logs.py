import sys
import os
import re
from datetime import datetime

def start_logging(log_dir="logs"):
    current_dir = os.getcwd()
    logs_path = os.path.join(current_dir, log_dir)
    os.makedirs(logs_path, exist_ok=True)

    next_id = get_next_log_id(logs_path)
    log_filename = f"system_log_withID{next_id:04d}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    log_path = os.path.join(logs_path, log_filename)

    sys.stdout = Logger(log_path)
    sys.stderr = sys.stdout

    print(f"[INFO] [LOG START] ID = {next_id:04d}")

def get_next_log_id(logs_path):
    existing = os.listdir(logs_path)
    ids = []
    for name in existing:
        m = re.search(r"withID(\d+)", name)
        if m:
            ids.append(int(m.group(1)))
    return max(ids, default=0) + 1

class Logger:
    def __init__(self, filename):
        self.terminal_stdout = sys.stdout
        self.terminal_stderr = sys.stderr
        self.log = open(filename, "a", buffering=1, encoding="utf-8")

    def write(self, message):
        self.terminal_stdout.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal_stdout.flush()
        self.log.flush()
