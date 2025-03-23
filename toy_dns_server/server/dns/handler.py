import socketserver
from dnslib import DNSRecord
from toy_dns_server.log.logger import Logger
from toy_dns_server.resolver.dns_resolver import DNSResolver

class DNSRequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self._logger = Logger(self)
        self._resolver: DNSResolver = self.server.resolver

    def handle(self):
        self._logger.debug("Handling DNS query")

        data, socket_instance = self.request
        client_ip, client_port = self.client_address

        self._logger.debug(f"Received DNS query from {client_ip}:{client_port}")

        try:
            dns_request = DNSRecord.parse(data)
            self._logger.debug(f"Parsed DNS request: {dns_request.q.qname}")

            response_data = self._resolver.resolve(data)

            socket_instance.sendto(response_data, self.client_address)
            self._logger.info(f"Responded to {client_ip}:{client_port}")

        except Exception as e:
            self._logger.error(f"Failed to handle DNS query from {client_ip}:{client_port}: {e}")
