import logging
import os
import sys
import traceback
from io import StringIO
from colorama import Fore, Style, init

init(autoreset=True)

DEFAULT_LOG_DIR = os.getenv("TOY_DNS_LOG_DIR", "/var/log/toy_dns_server")
DEFAULT_STDOUT_LOG = os.path.join(DEFAULT_LOG_DIR, "stdout.log")
DEFAULT_STDERR_LOG = os.path.join(DEFAULT_LOG_DIR, "stderr.log")

try:
    os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)
except PermissionError:
    fallback = "/tmp/toy_dns_server_logs"
    print(f"⚠ Warning: No permission to write logs in `{DEFAULT_LOG_DIR}`, using `{fallback}` instead.")
    DEFAULT_LOG_DIR = fallback
    DEFAULT_STDOUT_LOG = os.path.join(DEFAULT_LOG_DIR, "stdout.log")
    DEFAULT_STDERR_LOG = os.path.join(DEFAULT_LOG_DIR, "stderr.log")
    os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)

class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.BLUE,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        msg = super().format(record)
        return self.COLORS.get(record.levelname, "") + msg + Style.RESET_ALL

formatter = ColoredFormatter(
    "[%(asctime)s] [PID: %(process)d] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

log_buffer = StringIO()

logger = logging.getLogger("toy_dns_server")
logger.setLevel(logging.DEBUG)

buffer_handler = logging.StreamHandler(log_buffer)
buffer_handler.setLevel(logging.DEBUG)
buffer_handler.setFormatter(formatter)
logger.addHandler(buffer_handler)

stdout_handler = None
stderr_handler = None

def reconfigure_logger(config):
    global stdout_handler, stderr_handler

    logger.handlers = [buffer_handler]

    logger.setLevel(getattr(logging, config.logging.level.upper(), logging.INFO))

    if config.logging.stdout_log_file.lower() == "stdout":
        stdout_handler = logging.StreamHandler(sys.stdout)
    else:
        os.makedirs(os.path.dirname(config.logging.stdout_log_file), exist_ok=True)
        stdout_handler = logging.FileHandler(config.logging.stdout_log_file, mode='a')

    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)

    stderr_handler = logging.FileHandler(config.logging.stderr_log_file, mode='a')
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

def flush_logs(success=True):
    log_buffer.seek(0)
    logs = log_buffer.read()

    if success and stdout_handler:
        try:
            stdout_handler.stream.write(logs)
        except Exception:
            sys.stdout.write(logs)
    elif not success:
        print(Fore.RED + "\n===== APPLICATION CRASHED - DUMPING LOGS =====\n" + Style.RESET_ALL)
        sys.stderr.write(logs)

def catch_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            flush_logs(success=False)
            print(traceback.format_exc(), file=sys.stderr)
            sys.exit(1)
        finally:
            flush_logs(success=True)
    return wrapper
