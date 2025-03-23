import logging
import os
import sys
import traceback
from io import StringIO
from colorama import Fore, Style, init

init(autoreset=True)

DEFAULT_LOG_DIR = "/var/log/toy_dns_server"
DEFAULT_STDOUT_LOG = os.path.join(DEFAULT_LOG_DIR, "stdout.log")
DEFAULT_STDERR_LOG = os.path.join(DEFAULT_LOG_DIR, "stderr.log")

class LoggerManager:
    def __init__(self):
        self.log_buffer = StringIO()
        self.logger = logging.getLogger("toy_dns_server")
        self.logger.setLevel(logging.DEBUG)

        self.formatter = ColoredFormatter(
            "[%(asctime)s] [PID: %(process)d] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        self.buffer_handler = logging.StreamHandler(self.log_buffer)
        self.buffer_handler.setLevel(logging.DEBUG)
        self.buffer_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.buffer_handler)

        self.stdout_handler = None
        self.stderr_handler = None

    def reconfigure(self, config):
        """Reconfigures the logger after config is loaded."""
        self.logger.handlers = [self.buffer_handler]

        self.logger.setLevel(getattr(logging, config.level.upper(), logging.INFO))

        if config.stdout_log_file.lower() == "stdout":
            self.stdout_handler = logging.StreamHandler(sys.stdout)
        else:
            log_dir = os.path.dirname(config.stdout_log_file)
            os.makedirs(log_dir, exist_ok=True)
            self.stdout_handler = logging.FileHandler(config.stdout_log_file, mode='a')

        self.stdout_handler.setLevel(logging.INFO)
        self.stdout_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stdout_handler)

        log_dir = os.path.dirname(config.stderr_log_file)
        os.makedirs(log_dir, exist_ok=True)
        self.stderr_handler = logging.FileHandler(config.stderr_log_file, mode='a')
        self.stderr_handler.setLevel(logging.WARNING)
        self.stderr_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stderr_handler)

    def flush_logs(self, success=True):
        """Flush buffered logs. If success, send them to configured output.
           If failure, print everything to stderr at DEBUG level.
        """
        self.log_buffer.seek(0)
        logs = self.log_buffer.read()

        if success:
            self.stdout_handler.stream.write(logs)
        else:
            print(Fore.RED + "\n===== APPLICATION CRASHED - DUMPING LOGS =====\n" + Style.RESET_ALL)
            sys.stderr.write(logs)

        self.log_buffer.close()
        self.log_buffer = StringIO()
        self.buffer_handler.stream = self.log_buffer

class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.BLUE,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_msg = super().format(record)
        return self.COLORS.get(record.levelname, "") + log_msg + Style.RESET_ALL

# Create global logger manager instance
logger_manager = LoggerManager()
logger = logger_manager.logger

def reconfigure_logger(config):
    """Reconfigures the logger after config is loaded."""
    logger_manager.reconfigure(config)

def flush_logs(success=True):
    """Flush buffered logs. If success, send them to configured output.
       If failure, print everything to stderr at DEBUG level.
    """
    logger_manager.flush_logs(success)

def catch_exceptions(func):
    """Decorator to catch unhandled exceptions and dump logs."""
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
