from threading import Thread

from toy_dns_server.config.loader import ConfigLoader, ConfigSchema
from toy_dns_server.log.logger import Logger
from toy_dns_server.log.base_logger import base_logger
from toy_dns_server.server.dns.server import DNSServer
from toy_dns_server.server.doh.server import DoHServer

class Bootstraper():
    _logger: Logger
    _running: bool = False
    _config: ConfigSchema
    _dns_server: DNSServer
    _root_dir: str

    def __init__(self, root_dir: str):
        self._logger = Logger(self)
        self._root_dir = root_dir
        self._logger.info("Bootstraper initialized.")

    def run(self):
        if self._running:
            self._logger.fatal("Bootstraper is already running.")
            raise RuntimeError("Bootstraper is already running.")

        self._logger.info("Running bootstraper...")
        self._load_config()

        self._configure_logging()
        self._start_dns_server()
        self._start_doh_server()

        self._logger.info("Bootstraper finished.")

    def stop(self):
        self._logger.info("Stopping bootstraper...")
        if self.__dns_server is not None:
            self._logger.debug("Stopping DNS server...")
            self.__dns_server.stop()

        if self.__doh_server is not None:
            self._logger.debug("Stopping DoH server...")
            self.__doh_server.stop()

        self._logger.info("Bootstraper stopped.")

    def _load_config(self):
        try:
            config_loader = ConfigLoader(self._root_dir)
            self._config = config_loader.load_config()
        except Exception as e:
            self._logger.error(f"Failed to load configuration: {e}")
            base_logger.handle_configuration_error()
            raise e

    def _start_dns_server(self):
        if self._config.server.dns is None:
            self._logger.warn("No DNS server configuration provided. Skipping DNS server initialization.")
            return

        if not self._config.server.dns.enabled:
            self._logger.info("DNS server is disabled. Skipping DNS server initialization.")

        self._logger.info("Starting DNS server...")
        self.__dns_server = DNSServer(self._config)

        thread = Thread(target=self.__dns_server.run)
        thread.start()

    def _start_doh_server(self):
        if self._config.server.doh is None:
            self._logger.warn("No DoH server configuration provided. Skipping DoH server initialization.")
            return

        if not self._config.server.doh.enabled:
            self._logger.info("DoH server is disabled. Skipping DoH server initialization.")
            return

        if self._config.server.doh:
            self._logger.info("Starting DoH server...")
            self.__doh_server = DoHServer(self._config)

            thread = Thread(target=self.__doh_server.run)
            thread.start()

    def _configure_logging(self):
        base_logger.reconfigure_logger(self._config.logging)
