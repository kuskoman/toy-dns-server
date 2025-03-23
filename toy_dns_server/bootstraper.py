from threading import Thread

from toy_dns_server.config.loader import ConfigLoader, ConfigSchema
from toy_dns_server.log.logger import Logger
from toy_dns_server.log.base_logger import base_logger
from toy_dns_server.server.dns.server import DNSServer
from toy_dns_server.server.doh.server import DoHServer

class Bootstraper():
    __logger: Logger
    __running: bool = False
    __config: ConfigSchema
    __dns_server: DNSServer

    def __init__(self):
        self.__logger = Logger(self)
        self.__logger.info("Bootstraper initialized.")

    def run(self):
        if self.__running:
            self.__logger.fatal("Bootstraper is already running.")
            raise RuntimeError("Bootstraper is already running.")

        self.__logger.info("Running bootstraper...")
        config_loader = ConfigLoader()
        self.__config = config_loader.load_config()

        self.__configure_logging()
        self.__start_dns_server()
        self.__start_doh_server()

        self.__logger.info("Bootstraper finished.")

    def stop(self):
        self.__logger.info("Stopping bootstraper...")
        if self.__dns_server is not None:
            self.__logger.debug("Stopping DNS server...")
            self.__dns_server.stop()

        if self.__doh_server is not None:
            self.__logger.debug("Stopping DoH server...")
            self.__doh_server.stop()

        self.__logger.info("Bootstraper stopped.")

    def __start_dns_server(self):
        if self.__config.server.dns is None:
            self.__logger.warn("No DNS server configuration provided. Skipping DNS server initialization.")
            return

        if not self.__config.server.dns.enabled:
            self.__logger.info("DNS server is disabled. Skipping DNS server initialization.")

        self.__logger.info("Starting DNS server...")
        self.__dns_server = DNSServer(self.__config)

        thread = Thread(target=self.__dns_server.run)
        thread.start()

    def __start_doh_server(self):
        if self.__config.server.doh is None:
            self.__logger.warn("No DoH server configuration provided. Skipping DoH server initialization.")
            return

        if not self.__config.server.doh.enabled:
            self.__logger.info("DoH server is disabled. Skipping DoH server initialization.")
            return

        if self.__config.server.doh:
            self.__logger.info("Starting DoH server...")
            self.__doh_server = DoHServer(self.__config)

            thread = Thread(target=self.__doh_server.run)
            thread.start()

    def __configure_logging(self):
        base_logger.reconfigure_logger(self.__config.logging)
