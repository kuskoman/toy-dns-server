from toy_dns_server.config.schema import ConfigSchema
from toy_dns_server.server.doh.http_server import DoHHTTPServer
from toy_dns_server.server.doh.https_server import DoHHTTPSServer

from toy_dns_server.resolver.dns_resolver import DNSResolver

class DoHServer:
    _config: ConfigSchema
    _server = None

    def __init__(self, config: ConfigSchema):
        self._config = config
        self._server = None

    def run(self):
        doh_config = self._config.server.doh
        resolver_config = self._config.resolver
        resolver = DNSResolver(resolver_config)
        if doh_config.mode == "http":
            self._server = DoHHTTPServer(doh_config.http, resolver)
        elif doh_config.mode == "https":
            self._server = DoHHTTPSServer(doh_config.https, resolver)
        else:
            raise ValueError(f"Unsupported DoH mode: {doh_config.mode}")
        self._server.run()

    def stop(self):
        if self._server:
            self._server.stop()
