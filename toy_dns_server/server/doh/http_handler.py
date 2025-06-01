from http.server import BaseHTTPRequestHandler
import time
from toy_dns_server.log.logger import Logger
from toy_dns_server.resolver.dns_resolver import DNSResolver
from toy_dns_server.metrics.metrics import (
    dns_query_counter,
    dns_query_duration,
)
from dnslib import DNSRecord
import traceback

class DNSOverHTTPHandler(BaseHTTPRequestHandler):
    resolver: DNSResolver
    _logger: Logger

    def __init__(self, request, client_address, server):
        self._logger = Logger(self)
        super().__init__(request, client_address, server)
        
    def log_message(self, format, *args):
        """Override the default log_message to use our custom logger."""
        self._logger.info(format % args)

    def do_POST(self):
        start_time = time.time()
        metrics = self._handle_request()
        self._observe_metrics(metrics["qtype"], metrics["status"], start_time)



    def _handle_request(self):
        content_type = self.headers.get("Content-Type")
        if content_type != "application/dns-message":
            self.send_error(415, "Unsupported Media Type")
            return _error_response_metric

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length <= 0:
                self.send_error(400, "No DNS query data provided")
                return _error_response_metric

            if content_length > 65535:
                self.send_error(413, "Payload Too Large")
                return _error_response_metric

            query_data = self.rfile.read(content_length)
            if not query_data:
                self.send_error(400, "Empty DNS query data")
                return _error_response_metric

            self._logger.debug(f"Received DoH query from {self.client_address[0]}:{self.client_address[1]}")
            dns_request = DNSRecord.parse(query_data)
            self._logger.debug(f"Parsed DNS query: {dns_request.q.qname}")

            qtype = dns_request.q.qtype

            response_data = self.resolver.resolve(query_data)

            self.send_response(200)
            self.send_header("Content-Type", "application/dns-message")
            self.send_header("Content-Length", str(len(response_data)))
            self.end_headers()
            self.wfile.write(response_data)

            return {
                "qtype": qtype,
                "status": "success"
            }

        except Exception as e:
            self._logger.error(f"Failed to handle DoH query: {e}\n{traceback.format_exc()}")
            self.send_error(500, "Internal Server Error")
            return _error_response_metric


    def _observe_metrics(self, qtype: str, status: str, startTime: float):
        duration = time.time() - startTime
        self._logger.debug(f"Query duration: {duration:.2f} seconds")

        dns_query_counter.labels(
            query_type=qtype,
            status=status,
            handler_type="doh"
        ).inc()

        dns_query_duration.labels(
            query_type=qtype,
            status=status,
            handler_type="doh"
        ).observe(duration)

_error_response_metric = {
    "status": "error",
    "qtype": "0"
}
