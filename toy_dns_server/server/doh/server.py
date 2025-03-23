from toy_dns_server.config.schema import ConfigSchema
from toy_dns_server.server.doh.http_server import DoHHTTPServer
from toy_dns_server.server.doh.https_server import DoHHTTPSServer

from toy_dns_server.resolver.dns_resolver import DNSResolver

class DoHServer:
    __config: ConfigSchema

    def __init__(self, config: ConfigSchema):
        self.__config = config
        self.__server = None

    def run(self):
        doh_config = self.__config.server.doh
        resolver_config = self.__config.resolver
        resolver = DNSResolver(resolver_config)
        if doh_config.mode == "http":
            self._server = DoHHTTPServer(doh_config.http, resolver)
        elif doh_config.mode == "https":
            self._server = DoHHTTPSServer(doh_config.https, resolver)
        else:
            raise ValueError(f"Unsupported DoH mode: {doh_config.mode}")
        self._server.run()

    def stop(self):
        if self.__server:
            self.__server.stop()
