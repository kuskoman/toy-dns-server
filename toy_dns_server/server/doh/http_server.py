from http.server import ThreadingHTTPServer

from toy_dns_server.config.schema import DoHHTTPConfig
from toy_dns_server.log.logger import Logger
from toy_dns_server.resolver.dns_resolver import DNSResolver
from toy_dns_server.server.doh.doh_handler import make_doh_handler


class DoHHTTPServer:
    _logger: Logger

    def __init__(self, config: DoHHTTPConfig, resolver: DNSResolver):
        self._logger = Logger(self)
        self._logger.debug("Creating DoH HTTP server")
        host, port = config.listen_address.split(":")
        handler_cls = make_doh_handler(resolver)
        self._httpd = ThreadingHTTPServer((host, int(port)), handler_cls)

    def run(self):
        self._logger.info(f"Starting DoH HTTP server on {self._httpd.server_address}")
        self._httpd.serve_forever()

    def stop(self):
        self._logger.info("Stopping DoH HTTP server")
        self._httpd.shutdown()
        self._httpd.server_close()
        self._logger.info("DoH HTTP server stopped")
