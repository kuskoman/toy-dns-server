from posixpath import abspath
import ssl
from http.server import ThreadingHTTPServer

from toy_dns_server.log.logger import Logger
from toy_dns_server.config.schema import DoHHTTPSConfig
from toy_dns_server.resolver.dns_resolver import DNSResolver
from toy_dns_server.server.doh.doh_handler import make_doh_handler

class DoHHTTPSServer:
    _logger: Logger

    def __init__(self, config: DoHHTTPSConfig, resolver: DNSResolver):
        self._logger = Logger(self)
        self._logger.debug("Creating DoH HTTPS server")
        host, port = config.listen_address.split(":")

        handler_cls = make_doh_handler(resolver)
        self._httpd = ThreadingHTTPServer((host, int(port)), handler_cls)

        self._logger.debug("Wrapping HTTP server with SSL context")
        context = ssl.SSLContext(self._tls_version(config.security.min_tls_version))

        abs_certfile_path = abspath(config.security.certificate_file)
        abs_keyfile_path = abspath(config.security.key_file)
        self._logger.debug(f"Loading certificate from {abs_certfile_path}")
        self._logger.debug(f"Loading key from {abs_keyfile_path}")

        context.load_cert_chain(
            certfile=abs_certfile_path,
            keyfile=abs_keyfile_path
        )
        self._httpd.socket = context.wrap_socket(self._httpd.socket, server_side=True)

    def run(self):
        self._logger.info(f"Starting DoH HTTPS server on {self._httpd.server_address}")
        self._httpd.serve_forever()

    def stop(self):
        self._logger.info("Stopping DoH HTTPS server")
        self._httpd.shutdown()
        self._httpd.server_close()
        self._logger.info("DoH HTTPS server stopped")

    def _tls_version(self, version: str):
        if version == "TLS13":
            return ssl.PROTOCOL_TLSv1_3
        elif version == "TLS12":
            return ssl.PROTOCOL_TLSv1_2
        elif version == "TLS11":
            return ssl.PROTOCOL_TLSv1_1
        elif version == "TLS10":
            return ssl.PROTOCOL_TLSv1
        else:
            raise ValueError(f"Unsupported TLS version: {version}")
