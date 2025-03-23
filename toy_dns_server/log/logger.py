import logging

from toy_dns_server.log.base_logger import base_logger


class Logger:
    def __init__(self, classOrName):
        self.__name = classOrName if isinstance(classOrName, str) else type(classOrName).__name__
        self._logger = base_logger


    def debug(self, message: str):
        self._logger.log(message, logging.DEBUG, self.__name)

    def info(self, message: str):
        self._logger.log(message, logging.INFO, self.__name)

    def warn(self, message: str):
        self._logger.log(message, logging.WARNING, self.__name)

    def error(self, message: str):
        self._logger.log(message, logging.ERROR, self.__name)

    def fatal(self, message: str):
        self._logger.log(message, logging.CRITICAL, self.__name)
        raise RuntimeError(message)
