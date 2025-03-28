from http.server import BaseHTTPRequestHandler
from toy_dns_server.log.logger import Logger
from toy_dns_server.resolver.dns_resolver import DNSResolver
from dnslib import DNSRecord
import traceback

class DNSOverHTTPHandler(BaseHTTPRequestHandler):
    resolver: DNSResolver
    _logger: Logger

    def __init__(self, request, client_address, server):
        self._logger = Logger(self)
        super().__init__(request, client_address, server)

    def do_POST(self):
        content_type = self.headers.get("Content-Type")
        if content_type != "application/dns-message":
            self.send_error(415, "Unsupported Media Type")
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self.send_error(400, "No DNS query data provided")
                return

            query_data = self.rfile.read(content_length)
            if not query_data:
                self.send_error(400, "Empty DNS query data")
                return

            self._logger.debug(f"Received DoH query from {self.client_address[0]}:{self.client_address[1]}")
            dns_request = DNSRecord.parse(query_data)
            self._logger.debug(f"Parsed DNS query: {dns_request.q.qname}")

            response_data = self.resolver.resolve(query_data)

            self.send_response(200)
            self.send_header("Content-Type", "application/dns-message")
            self.send_header("Content-Length", str(len(response_data)))
            self.end_headers()
            self.wfile.write(response_data)

        except Exception as e:
            self._logger.error(f"Failed to handle DoH query: {e}\n{traceback.format_exc()}")
            self.send_error(500, "Internal Server Error")


    def log_message(self, format, *args):
        self._logger.debug(format % args)
        return

