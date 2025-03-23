import socket
import random

from toy_dns_server.log.logger import Logger
from toy_dns_server.config.schema import ResolverConfig

class DNSResolver:
    _logger: Logger
    _timeout_seconds: float
    _upstream_servers: list[str]

    def __init__(self, config: ResolverConfig):
        self._logger = Logger(self)
        upstream_config = config.upstream
        self._timeout_seconds = upstream_config.timeout_ms / 1000
        self._upstream_servers = upstream_config.servers

    def resolve(self, query: bytes) -> bytes:
        servers = self._upstream_servers[:]
        random.shuffle(servers)

        for server in servers:
            self._logger.debug(f"Attempting to forward query to upstream server: {server}")
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.settimeout(self._timeout_seconds)
                    sock.sendto(query, (server, 53))
                    response, _ = sock.recvfrom(4096)
                    return response
            except (socket.timeout, socket.error) as e:
                self._logger.warning(f"Failed to get response from server {server}: {e}")

        self._logger.fatal("All upstream servers failed to respond")
