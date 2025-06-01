import socket
import random
import asyncio
import concurrent.futures
from typing import Optional, Union, Tuple
from dnslib import DNSRecord, EDNS0, RCODE, DNSHeader, RR, QTYPE, EDNSOption, DNSLabel


from toy_dns_server.log.logger import Logger
from toy_dns_server.config.schema import CacheConfig, ResolverConfig
from toy_dns_server.cache.cache import DNSCache
from toy_dns_server.security.dnssec import DNSSECValidator
from toy_dns_server.metrics.metrics import (
    dnssec_validation_counter
)


class DNSResolver:
    _logger: Logger
    _timeout_seconds: float
    _upstream_servers: list[str]
    _cache: Union[DNSCache, None] = None
    _dnssec_validator: Optional[DNSSECValidator] = None

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

        if config.security.dnssec_validation:
            self._logger.info("DNSSEC validation is enabled")
            self._dnssec_validator = DNSSECValidator()


    def resolve(self, original_query: bytes) -> bytes:
        record = DNSRecord.parse(original_query)
        cached_response = self._get_from_cache(record)
        if cached_response:
            return self._return_cached_response(cached_response, record)

        if self._dnssec_validator:
            return self._resolve_with_dnssec_fallback(record)
        else:
            return self._query_upstream(record, record.pack(), validate_dnssec=False)


    async def _query_server_async(self, server: str, packed_query: bytes, timeout: float):
        try:
            loop = asyncio.get_event_loop()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)

            await loop.sock_sendto(sock, packed_query, (str(server), 53))
            response, _ = await loop.sock_recvfrom(sock, 4096)
            sock.close()
            return response
        except (socket.timeout, socket.error, asyncio.TimeoutError) as e:
            self._logger.warn(f"Failed to get async response from server {server}: {e}")
            return None

    def _resolve_with_dnssec_fallback(self, record: DNSRecord) -> bytes:
        regular_record = DNSRecord.parse(record.pack())
        dnssec_record = DNSRecord.parse(record.pack())
        self._append_edns0(dnssec_record)

        regular_query = regular_record.pack()
        dnssec_query = dnssec_record.pack()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            server = random.choice(self._upstream_servers)

            tasks = [
                loop.create_task(self._query_server_async(server, regular_query, self._timeout_seconds)),
                loop.create_task(self._query_server_async(server, dnssec_query, self._timeout_seconds))
            ]

            done, pending = loop.run_until_complete(asyncio.wait(
                tasks,
                timeout=self._timeout_seconds,
                return_when=asyncio.FIRST_COMPLETED
            ))

            for task in pending:
                task.cancel()

            if not done:
                return self._build_servfail_response(record, 0, len(self._upstream_servers))

            for task in done:
                response = task.result()
                if not response:
                    continue

                try:
                    response_record = DNSRecord.parse(response)
                    if response_record and len(response_record.rr) > 0:
                        self._set_to_cache(record, response)
                        return response
                except Exception as e:
                    self._logger.warn(f"Failed to parse response: {e}")

            return self._query_upstream(record, regular_query, validate_dnssec=False)
        finally:
            loop.close()

    def _query_upstream(self, record: DNSRecord, packed_query: bytes, validate_dnssec: bool = True) -> bytes:
        failed_dnssec = 0
        failed_to_resolve = 0
        servers = self._upstream_servers[:]
        random.shuffle(servers)

        for server in servers:
            self._logger.debug(f"Attempting to forward query to upstream server: {server}")
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.settimeout(self._timeout_seconds)
                    sock.sendto(packed_query, (str(server), 53))
                    response, _ = sock.recvfrom(4096)

                    if validate_dnssec and self._dnssec_validator:
                        if not self._dnssec_validator.validate(response):
                            self._logger.warn("DNSSEC validation failed")
                            failed_dnssec += 1
                            dnssec_validation_counter.labels("failed").inc()
                            continue
                        else:
                            dnssec_validation_counter.labels("success").inc()

                    self._set_to_cache(record, response)
                    return response

            except (socket.timeout, socket.error) as e:
                self._logger.warn(f"Failed to get response from server {server}: {e}")
                failed_to_resolve += 1

        return self._build_servfail_response(record, failed_dnssec, failed_to_resolve)

    def _build_servfail_response(self, record: DNSRecord, failed_dnssec: int, failed_to_resolve: int) -> bytes:
        self._logger.error(
            f"Failed to resolve query {record.q.qname}. "
            f"Failed DNSSEC: {failed_dnssec}, Failed to resolve: {failed_to_resolve}"
        )
        servfail = DNSRecord(
            DNSHeader(id=record.header.id, qr=1, ra=1, rcode=RCODE.SERVFAIL),
            q=record.q
        )
        return servfail.pack()

    def _return_cached_response(self, cached: DNSRecord, original: DNSRecord) -> bytes:
        cached.header.id = original.header.id
        return cached.pack()

    def _append_edns0(self, record: DNSRecord):
        rname = record.q.qname
        opt = EDNS0(rname,
                    flags="do", # DNSSEC OK
                    # ext_rcode=0, # no extended error codes
                    # ext_rcode=1, # return extended error codes
                    ext_rcode=1,
                    udp_len=4096,
                    version=1, # EDNS version
                    opts=[EDNSOption(1,b'')] # todo: figure out what is 1 responsible for
                )
        record.add_ar(opt)

    def _initialize_cache(self, cache_config: CacheConfig):
        if not cache_config.enabled:
            self._logger.info("DNS cache is disabled")
            return

        self._cache = DNSCache(cache_config.ttl_seconds, cache_config.max_entries)
        self._logger.info("DNS cache initialized")

    def _get_from_cache(self, record: DNSRecord) -> Optional[DNSRecord]:
        if not self._cache:
            return None

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
