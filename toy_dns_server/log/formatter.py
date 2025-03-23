import logging
from colorama import Fore, Style

DEFAULT_LOG_FORMAT = "[%(asctime)s] [PID: %(process)d] [%(logger_name)s] [%(levelname)s] %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


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
