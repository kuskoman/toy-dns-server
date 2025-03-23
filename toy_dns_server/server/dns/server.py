import socketserver

from toy_dns_server.log.logger import Logger
from toy_dns_server.resolver.dns_resolver import DNSResolver
from toy_dns_server.server.dns.handler import DNSRequestHandler

from toy_dns_server.config.schema import ConfigSchema

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    daemon_threads = True
    allow_reuse_address = True

class DNSServer:
    __logger: Logger
    __resolver: DNSResolver
    __server: ThreadedUDPServer

    def __init__(self, config: ConfigSchema):
        dns_server_config = config.server.dns
        resolver_config = config.resolver
        host, port_str = dns_server_config.address.split(":")
        port = int(port_str)

        self.__logger = Logger(self)
        self.__resolver = DNSResolver(resolver_config)
        self.__server = ThreadedUDPServer((host, port), lambda *args: DNSRequestHandler(self.__resolver))

    def run(self):
        self.__logger.info(f"Starting DNS server on {self.__server.server_address}")
        self.__server.serve_forever()

    def stop(self):
        self.__logger.info("Stopping DNS server")
        self.__server.shutdown()
        self.__server.server_close()
        self.__logger.info("DNS server stopped")
