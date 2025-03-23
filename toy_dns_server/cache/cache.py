import time
from typing import Literal, Optional, Union

from dnslib import DNSRecord
from toy_dns_server.log.logger import Logger

class DNSCache:
    def __init__(self, ttl_seconds: Union[int, Literal["auto"]], max_entries: int):
        self._logger = Logger(self)
        self._use_auto_ttl = ttl_seconds == "auto"
        self._default_ttl = ttl_seconds if isinstance(ttl_seconds, int) else None
        self._max_entries = max_entries
        self._store: dict[str, tuple[bytes, float]] = {}

        self._logger.info(f"DNS cache initialized with max entries: {max_entries}")

    def set(self, key: str, response_data: bytes):
        record = DNSRecord.parse(response_data)
        min_ttl = min([rr.ttl for rr in record.rr]) if record.rr else None
        if min_ttl is None:
            self._logger.warn(f"TTL is None, not caching response for key: {key}")
            return

        expire_at = time.time() + min_ttl
        self._ensure_store_capacity()

        self._store[key] = (response_data, expire_at)
        self._logger.debug(f"Added entry {key} to cache with TTL {min_ttl}s")

    def get(self, key: str) -> Optional[DNSRecord]:
        entry = self._store.get(key)
        if not entry:
            self._logger.debug(f"No entry found in cache for key: {key}")
            return None

        response_data, expires_at = entry
        if time.time() >= expires_at:
            self._logger.debug(f"Entry for {key} has expired")
            del self._store[key]
            return None

        self._logger.debug(f"Entry for {key} found in cache")
        return self._format_response(response_data, expires_at)

    def _format_response(self, response_data: bytes, expires_at) -> DNSRecord:
        record = DNSRecord.parse(response_data)
        self._adjust_ttl(record, expires_at)
        return record

    def _adjust_ttl(self, record: DNSRecord, expires_at) -> DNSRecord:
        now = time.time()
        remaining_ttl = max(0, int(expires_at - now - 1))

        for section in [record.rr, record.auth, record.ar]:
            for rr in section:
                rr.ttl = remaining_ttl

        return record


    def _ensure_store_capacity(self):
        if len(self._store) >= self._max_entries:
            self._delete_expired_entries()

        if len(self._store) >= self._max_entries:
            self._delete_entry_with_closest_expiration()

    def _delete_entry_with_closest_expiration(self):
        self._logger.warn("Cache is full, removing entry with the closest expiration time")
        min_key = min(self._store, key=lambda k: self._store[k][1])
        del self._store[min_key]

    def _delete_expired_entries(self):
        self._logger.debug("Deleting expired cache entries")
        now = time.time()
        expired_keys = [k for k, (_, t) in self._store.items() if now >= t]
        for k in expired_keys:
            del self._store[k]

# class DNSCache:
#     def __init__(self, ttl_seconds: Union[int, Literal["auto"]], max_entries: int):
#         self._logger = Logger(self)
#         self._use_auto_ttl = ttl_seconds == "auto"
#         self._default_ttl = ttl_seconds if isinstance(ttl_seconds, int) else None
#         self._max_entries = max_entries
#         self._store: dict[str, tuple[bytes, float]] = {}

#         self._logger.info(f"DNS cache initialized with max entries: {max_entries}")

#     def get(self, key: str) -> Optional[bytes]:
#         self._logger.debug(f"Getting entry from cache for key: {key}")
#         entry = self._store.get(key)
#         if entry:
#             response_data, expire_at = entry
#             if time.time() < expire_at:
#                 self._logger.debug(f"Entry for {key} found in cache")
#                 return response_data
#             else:
#                 self._logger.debug(f"Entry for {key} has expired")
#                 del self._store[key]
#         else:
#             self._logger.debug(f"No entry found in cache for key: {key}")
#         return None

#     def set(self, key: str, response_data: bytes):
#         self._logger.debug(f"Setting entry in cache for key: {key}")
#         ttl = self._extract_min_ttl(response_data) if self._use_auto_ttl else self._default_ttl
#         if ttl is None:
#             self._logger.warn(f"TTL is None, not caching response for key: {key}")
#             return

#         expire_at = time.time() + ttl

#         if len(self._store) >= self._max_entries:
#             self._delete_expired_entries()

#         if len(self._store) >= self._max_entries:
#             self._logger.warn("Cache is full, removing entry with the closest expiration time")
#             min_key = min(self._store, key=lambda k: self._store[k][1])
#             del self._store[min_key]

#         self._store[key] = (response_data, expire_at)
#         self._logger.debug(f"Added entry to cache with TTL {ttl}s")

#     def _extract_min_ttl(self, response_data: bytes) -> Optional[int]:
#         self._logger.debug("Extracting minimum TTL from DNS response")
#         try:
#             record = DNSRecord.parse(response_data)
#             ttls = [rr.ttl for rr in record.rr]
#             return min(ttls) if ttls else None
#         except Exception as e:
#             self._logger.warn(f"Failed to extract minimum TTL: {e}")
#             return None

#     def _delete_expired_entries(self):
#         self._logger.debug("Deleting expired cache entries")
#         now = time.time()
#         expired_keys = [k for k, (_, t) in self._store.items() if now >= t]
#         for k in expired_keys:
#             del self._store[k]
