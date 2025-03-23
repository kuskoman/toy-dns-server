import socket
import random
from typing import Optional, Union
from dnslib import DNSRecord


from toy_dns_server.log.logger import Logger
from toy_dns_server.config.schema import CacheConfig, ResolverConfig
from toy_dns_server.cache.cache import DNSCache


class DNSResolver:
    _logger: Logger
    _timeout_seconds: float
    _upstream_servers: list[str]
    _cache: Union[DNSCache, None] = None

    def __init__(self, config: ResolverConfig):
        self._logger = Logger(self)
        upstream_config = config.upstream
        self._timeout_seconds = upstream_config.timeout_ms / 1000
        self._upstream_servers = upstream_config.servers

        if config.cache is None:
            self._logger.warn("No cache configuration provided")

        if config.cache.enabled:
            self._logger.info("DNS cache is enabled")
            self._initialize_cache(config.cache)

    def resolve(self, query: bytes) -> bytes:
        record = DNSRecord.parse(query)
        cached_response = self._get_from_cache(query)
        if cached_response:
            cached_response.header.id = record.header.id
            return cached_response.pack()

        servers = self._upstream_servers[:]
        random.shuffle(servers)

        for server in servers:
            self._logger.debug(f"Attempting to forward query to upstream server: {server}")
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.settimeout(self._timeout_seconds)
                    server_str = str(server)
                    sock.sendto(query, (server_str, 53))
                    response, _ = sock.recvfrom(4096)
                    self._set_to_cache(record, response)
                    return response
            except (socket.timeout, socket.error) as e:
                self._logger.warn(f"Failed to get response from server {server}: {e}")

        self._logger.fatal("All upstream servers failed to respond")

    def _initialize_cache(self, cache_config: CacheConfig):
        if not cache_config.enabled:
            self._logger.info("DNS cache is disabled")
            return

        self._cache = DNSCache(cache_config.ttl_seconds, cache_config.max_entries)
        self._logger.info("DNS cache initialized")

    def _get_from_cache(self, query: bytes) -> Optional[DNSRecord]:
        if not self._cache:
            return None

        record = DNSRecord.parse(query)

        key = self._query_cache_key(record)
        if not key:
            return None

        response_data = self._cache.get(key)
        if response_data:
            self._logger.debug("Cache hit")
            return response_data

        self._logger.debug("Cache miss")
        return None

    def _set_to_cache(self, query: DNSRecord, response_data: bytes):
        if not self._cache:
            return

        key = self._query_cache_key(query)
        if not key:
            return

        self._cache.set(key, response_data)
        self._logger.debug("Cached response")


    def _query_cache_key(self, record: DNSRecord) -> Optional[str]:
        try:
            q = record.q
            return f"{str(q.qname)}|{q.qtype}|{q.qclass}"
        except Exception as e:
            self._logger.warn(f"Failed to parse DNS query for cache key: {e}")
            return None
