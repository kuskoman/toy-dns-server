from prometheus_client import start_http_server
from toy_dns_server.config.schema import ConfigSchema, MetricsExporterConfig

class Exporter:
    def __init__(self, config: MetricsExporterConfig):
        self._config = config

    def run(self):
        address, port = self._config.listen_address.split(":")
        port = int(port)
        start_http_server(port, addr=address)
