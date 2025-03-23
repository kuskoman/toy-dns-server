import logging

from toy_dns_server.log.base_logger import base_logger


class Logger:
    def __init__(self, classOrName):
        self.__name = classOrName if isinstance(classOrName, str) else type(classOrName).__name__
        self.__logger = base_logger

    def debug(self, message: str):
        self.__logger.log(message, logging.DEBUG, self.__name)

    def info(self, message: str):
        self.__logger.log(message, logging.INFO, self.__name)

    def warn(self, message: str):
        self.__logger.log(message, logging.WARNING, self.__name)

    def error(self, message: str):
        self.__logger.log(message, logging.ERROR, self.__name)
