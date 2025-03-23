from toy_dns_server.config.loader import ConfigLoader
from toy_dns_server.log.logger import Logger
from toy_dns_server.log.base_logger import base_logger

class Bootstraper():
    __logger: Logger
    __running: bool = False

    def __init__(self):
        self.__logger = Logger(self)
        self.__logger.info("Bootstraper initialized.")

    def run(self):
        if self.__running:
            self.__logger.error("Bootstraper is already running.")
            raise RuntimeError("Bootstraper is already running.")

        self.__logger.info("Running bootstraper...")
        config_loader = ConfigLoader()
        config = config_loader.load_config()
        base_logger.reconfigure_logger(config.logging)
        self.__logger.info("Bootstraper finished.")
