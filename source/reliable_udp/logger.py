import sys
import datetime
import os

def make_logger(filename):
    os.makedirs("logs", exist_ok=True)
    f = open(f"logs/{filename}", "a")

    def log(msg):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] {msg}"
        print(formatted, file=sys.stderr)
        f.write(formatted + "\n")
        f.flush()

    return log
