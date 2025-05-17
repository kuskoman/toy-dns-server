import socketserver

from toy_dns_server.log.logger import Logger
from toy_dns_server.resolver.dns_resolver import DNSResolver
from toy_dns_server.server.dns.handler import DNSRequestHandler
from toy_dns_server.config.schema import ConfigSchema

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass, resolver: DNSResolver):
        self.resolver = resolver  # Inject resolver into handler
        super().__init__(server_address, RequestHandlerClass)


class DNSServer:
    _logger: Logger
    _resolver: DNSResolver
    _server: ThreadedUDPServer

    def __init__(self, config: ConfigSchema):
        dns_server_config = config.server.dns
        resolver_config = config.resolver
        host, port_str = dns_server_config.address.split(":")
        port = int(port_str)

        self._logger = Logger(self)
        self._resolver = DNSResolver(resolver_config)
        self._server = ThreadedUDPServer(
            (host, port),
            DNSRequestHandler,
            self._resolver
        )

    def run(self):
        self._logger.info(f"Starting DNS server on {self._server.server_address}")
        self._server.serve_forever()

    def stop(self):
        self._logger.info("Stopping DNS server")
        self._server.shutdown()
        self._server.server_close()
        self._logger.info("DNS server stopped")
