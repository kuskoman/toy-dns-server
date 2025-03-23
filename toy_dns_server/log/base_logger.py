import logging
import os
import sys
from typing import List, Tuple

from toy_dns_server.config.schema import LoggingConfig
from toy_dns_server.log.formatter import DEFAULT_DATE_FORMAT, DEFAULT_LOG_FORMAT, ColoredFormatter

class BaseLogger:
    DEFAULT_LOG_DIR = os.getenv("TOY_DNS_LOG_DIR", "/var/log/toy_dns_server")
    DEFAULT_STDOUT_LOG = "stdout"
    DEFAULT_STDERR_LOG = "stderr"

    def __init__(self):
        self.__stdout_logger = logging.getLogger("stdout")
        self.__stderr_logger = logging.getLogger("stderr")
        self.__stdout_logger.setLevel(logging.DEBUG)
        self.__stderr_logger.setLevel(logging.DEBUG)

        self.__log_formatter = ColoredFormatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
        self.__log_buffer: List[Tuple[str, int, str]] = []

        self.__stdout_log_path = self.DEFAULT_STDOUT_LOG
        self.__stderr_log_path = self.DEFAULT_STDERR_LOG
        self.__log_dir_created = False
        self.__reconfigured = False

    def __get_default_config(self) -> LoggingConfig:
        return LoggingConfig(
            level="debug",
            stdout_log_file=self.DEFAULT_STDOUT_LOG,
            stderr_log_file=self.DEFAULT_STDERR_LOG,
            log_format=DEFAULT_LOG_FORMAT,
            date_format=DEFAULT_DATE_FORMAT,
        )

    def __create_log_dirs(self):
        if self.__log_dir_created:
            return

        for path in [self.__stdout_log_path, self.__stderr_log_path]:
            if path not in ("stdout", "stderr"):
                os.makedirs(os.path.dirname(path), exist_ok=True)

        self.__log_dir_created = True

    def handle_configuration_error(self):
        config = self.__get_default_config()
        self.reconfigure_logger(config)
        self.__flush_logs()

    def log(self, message: str, level: int, logger_name: str):
        if not self.__reconfigured:
            self.__log_buffer.append((message, level, logger_name))
            return

        if level >= logging.WARNING:
            self.__stderr_logger.log(level, message, extra={"logger_name": logger_name})
        else:
            self.__stdout_logger.log(level, message, extra={"logger_name": logger_name})

    def reconfigure_logger(self, config: LoggingConfig):
        self.__stdout_log_path = config.stdout_log_file
        self.__stderr_log_path = config.stderr_log_file
        self.__log_formatter = ColoredFormatter(config.log_format, config.date_format)

        self.__create_log_dirs()

        self.__stdout_logger.handlers.clear()
        self.__stderr_logger.handlers.clear()

        if self.__stderr_log_path.lower() == "stderr":
            handler = logging.StreamHandler(sys.stderr)
        else:
            handler = logging.FileHandler(self.__stderr_log_path, mode="a")
        handler.setLevel(getattr(logging, config.level.upper()))
        handler.setFormatter(self.__log_formatter)
        self.__stderr_logger.addHandler(handler)

        if self.__stdout_log_path.lower() == "stdout":
            handler = logging.StreamHandler(sys.stdout)
        else:
            handler = logging.FileHandler(self.__stdout_log_path, mode="a")
        handler.setLevel(getattr(logging, config.level.upper()))
        handler.setFormatter(self.__log_formatter)
        self.__stdout_logger.addHandler(handler)

        self.__reconfigured = True
        self.__flush_logs()

    def __flush_logs(self):
        for message, level, logger_name in self.__log_buffer:
            self.log(message, level, logger_name)
        self.__log_buffer.clear()


base_logger = BaseLogger()
