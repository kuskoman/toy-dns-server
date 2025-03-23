import socketserver
from dnslib import DNSRecord

from toy_dns_server.log.logger import Logger

from toy_dns_server.resolver.dns_resolver import DNSResolver

class DNSRequestHandler(socketserver.BaseRequestHandler):
    __logger: Logger
    __resolver: DNSResolver

    def __init__(self, resolver: DNSResolver):
        self.__logger = Logger(self)
        self.__resolver = resolver

    def handle(self):
        data, socket_instance = self.request
        client_ip, client_port = self.client_address

        self.__logger.info(f"Received DNS query from {client_ip}:{client_port}")

        try:
            dns_request = DNSRecord.parse(data)
            self.__logger.debug(f"Parsed DNS request: {dns_request.q.qname}")

            response_data = self.__resolver.resolve(data)

            socket_instance.sendto(response_data, self.client_address)
            self.__logger.info(f"Responded to {client_ip}:{client_port}")

        except Exception as e:
            self.__logger.error(f"Failed to handle DNS query from {client_ip}:{client_port}: {e}")
