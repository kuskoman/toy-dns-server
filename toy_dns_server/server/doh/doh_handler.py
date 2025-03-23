from toy_dns_server.resolver.dns_resolver import DNSResolver
from toy_dns_server.server.doh.http_handler import DNSOverHTTPHandler


def make_doh_handler(resolver: DNSResolver):
    class CustomDoHHandler(DNSOverHTTPHandler):
        pass
    CustomDoHHandler.resolver = resolver
    return CustomDoHHandler
