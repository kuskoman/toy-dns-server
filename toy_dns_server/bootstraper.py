from concurrent.futures import ThreadPoolExecutor, as_completed
import time

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
    _executor: ThreadPoolExecutor
    _futures: list = []

    def __init__(self, root_dir: str):
        self._logger = Logger(self)
        self._root_dir = root_dir
        self._executor = ThreadPoolExecutor(max_workers=2)  # One for DNS, one for DoH
        self._logger.info("Bootstraper initialized.")

    def run(self):
        """
        Run the bootstraper and blocks execution until the bootstraper is stopped.

        Raises:
            RuntimeError: If the bootstraper is already running.
        """
        if self._running:
            self._logger.fatal("Bootstraper is already running.")
            raise RuntimeError("Bootstraper is already running.")

        self._logger.info("Running bootstraper...")
        self._load_config()

        self._configure_logging()
        self._start_dns_server()
        self._start_doh_server()

        self._logger.info("Bootstraper finished.")
        self._monitor_threads()

    def stop(self):
        self._logger.info("Stopping bootstraper...")
        if self.__dns_server is not None:
            self._logger.debug("Stopping DNS server...")
            self.__dns_server.stop()

        if self.__doh_server is not None:
            self._logger.debug("Stopping DoH server...")
            self.__doh_server.stop()

        self._logger.debug("Shutting down thread pool executor...")
        self._executor.shutdown(wait=True)
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

        future = self._executor.submit(self.__dns_server.run)
        self._futures.append(future)

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

            future = self._executor.submit(self.__doh_server.run)
            self._futures.append(future)

    def _configure_logging(self):
        base_logger.reconfigure_logger(self._config.logging)

    def _monitor_threads(self):
        self._logger.debug("Monitoring threads...")
        try:
            for future in as_completed(self._futures):
                try:
                    future.result()  # This will raise an exception if the thread failed
                except Exception as e:
                    self._logger.error(f"One of the threads failed: {e}")
                    self.stop()
                    return
        except KeyboardInterrupt:
            self._logger.debug("Received KeyboardInterrupt. Stopping thread monitoring.")
            self.stop()

        finally:
            self._logger.debug("Thread monitoring finished.")
