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
        start = time.time()
        data, socket_instance = self.request
        client_ip, client_port = self.client_address

        self._logger.debug("Handling DNS query")
        self._logger.debug(f"Received DNS query from {client_ip}:{client_port}")

        try:
            dns_request = DNSRecord.parse(data)
            qname = str(dns_request.q.qname)
            qtype = dns_request.q.qtype

            self._logger.debug(f"Parsed DNS request: {qname}")

            response_data = self._resolver.resolve(data)
            socket_instance.sendto(response_data, self.client_address)

            self._logger.info(f"Responded to {client_ip}:{client_port}")
            self._observe_metrics(qtype, "success", start)

        except Exception as e:
            self._logger.error(f"Failed to handle DNS query from {client_ip}:{client_port}: {e}")
            self._observe_metrics("0", "error", start)

    def _observe_metrics(self, qtype: str, status: str, startTime: float):
        duration = time.time() - startTime
        self._logger.debug(f"Query duration: {duration:.2f} seconds")

        dns_query_counter.labels(
            query_type=qtype,
            status=status,
            handler_type="dns"
        ).inc()

        dns_query_duration.labels(
            query_type=qtype,
            status=status,
            handler_type="dns"
        ).observe(duration)
