import socketserver
import time
from dnslib import DNSRecord

from toy_dns_server.log.logger import Logger
from toy_dns_server.resolver.dns_resolver import DNSResolver
from toy_dns_server.metrics.metrics import (
    dns_query_counter,
    dns_query_duration,
)


class DNSRequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self._logger = Logger(self)
        self._resolver: DNSResolver = self.server.resolver

    def handle(self):
        start_time = time.time()
        data, socket_instance = self.request
        client_ip, _ = self.client_address

        self._logger.debug("Handling DNS query")
        self._logger.debug(f"Received DNS query from {client_ip}")

        try:
            dns_request = DNSRecord.parse(data)
            self._logger.debug(f"Parsed DNS request: {dns_request.q.qname}")

            response_data = self._resolver.resolve(data)
            socket_instance.sendto(response_data, self.client_address)
            self._logger.info(f"Responded to {client_ip}")

            self._record_metrics(client_ip, start_time)

        except Exception as e:
            self._logger.error(f"Failed to handle DNS query from {client_ip}: {e}")
            self._record_metrics(client_ip, start_time)

    def _record_metrics(self, source: str, start_time: float):
        dns_query_counter.labels(protocol="udp", source=source).inc()
        dns_query_duration.observe(time.time() - start_time)
