from pydantic import BaseModel, Field, IPvAnyAddress
from typing import List, Literal


class DNSConfig(BaseModel):
    enabled: bool = Field(..., description="Enable DNS server")
    address: str = Field(..., description="DNS listening address in IP:PORT format")


class DoHHTTPConfig(BaseModel):
    listen_address: str = Field(..., description="Listen address for DoH HTTP mode")


class DoHTTPSecurityConfig(BaseModel):
    certificate_file: str = Field(..., description="Path to TLS certificate")
    key_file: str = Field(..., description="Path to TLS private key")
    min_tls_version: Literal["TLS12", "TLS13"] = Field(..., description="Minimum TLS version")
    max_tls_version: Literal["TLS12", "TLS13"] = Field(..., description="Maximum TLS version")


class DoHHTTPSConfig(BaseModel):
    listen_address: str = Field(..., description="Listen address for DoH HTTPS mode")
    security: DoHTTPSecurityConfig


class DoHConfig(BaseModel):
    mode: Literal["http", "https"] = Field(..., description="Mode: 'http' or 'https'")
    http: DoHHTTPConfig
    https: DoHHTTPSConfig


class ServerConfig(BaseModel):
    dns: DNSConfig
    doh: DoHConfig


class UpstreamConfig(BaseModel):
    servers: List[IPvAnyAddress] = Field(..., description="List of upstream DNS resolvers")
    timeout_ms: int = Field(..., gt=0, description="Timeout for upstream DNS queries in milliseconds")


class CacheConfig(BaseModel):
    enabled: bool
    ttl_seconds: int
    max_entries: int


class ResolverSecurityConfig(BaseModel):
    dnssec_validation: bool


class ResolverConfig(BaseModel):
    upstream: UpstreamConfig
    cache: CacheConfig
    security: ResolverSecurityConfig


class LoggingConfig(BaseModel):
    level: Literal["debug", "info", "warn", "error"] = Field(..., description="Logging level")
    stdout_log_file: str = Field(..., description="Path to stdout log file")
    stderr_log_file: str = Field(..., description="Path to stderr log file")
    log_format: str = Field(..., description="Log format")
    date_format: str = Field(..., description="Date format")


class MetricsExporterConfig(BaseModel):
    listen_address: str


class MetricsConfig(BaseModel):
    enabled: bool
    exporter: MetricsExporterConfig


class ConfigSchema(BaseModel):
    server: ServerConfig
    resolver: ResolverConfig
    logging: LoggingConfig
    metrics: MetricsConfig
