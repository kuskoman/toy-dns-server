from toy_dns_server.resolver.dns_resolver import DNSResolver
from toy_dns_server.server.doh.http_handler import DNSOverHTTPHandler

from toy_dns_server.log.logger import Logger


def make_doh_handler(resolver: DNSResolver):
    logger = Logger("DoHHandler factory")
    logger.debug("Creating DoHHandler class")
    class CustomDoHHandler(DNSOverHTTPHandler):
        pass
    CustomDoHHandler.resolver = resolver
    return CustomDoHHandler
