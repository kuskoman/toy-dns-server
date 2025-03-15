from pydantic import BaseModel, Field, FilePath, IPvAnyAddress
from typing import List

class DNSConfig(BaseModel):
    address: str = Field(..., description="DNS listening address in IP:PORT format")

class DoHHTTPConfig(BaseModel):
    listen_address: str = Field(..., description="Listen address for DoH HTTP mode")

class DoHHTTPSecurityConfig(BaseModel):
    certificate_file: FilePath = Field(..., description="Path to TLS certificate")
    key_file: FilePath = Field(..., description="Path to TLS private key")
    min_tls_version: str = Field(..., description="Minimum TLS version")
    max_tls_version: str = Field(..., description="Maximum TLS version")

class DoHHTTPSConfig(BaseModel):
    listen_address: str = Field(..., description="Listen address for DoH HTTPS mode")
    security: DoHHTTPSecurityConfig

class DoHConfig(BaseModel):
    mode: str = Field(..., pattern="^(http|https)$", description="Mode: 'http' or 'https'")
    http: DoHHTTPConfig
    https: DoHHTTPSConfig

class ResolverUpstreamConfig(BaseModel):
    servers: List[IPvAnyAddress] = Field(..., description="List of upstream DNS resolvers")
    timeout_ms: int = Field(..., gt=0, description="Timeout for upstream DNS queries in milliseconds")

class ResolverCacheConfig(BaseModel):
    enabled: bool
    ttl_seconds: int
    max_entries: int

class ResolverSecurityConfig(BaseModel):
    dnssec_validation: bool

class ResolverConfig(BaseModel):
    upstream: ResolverUpstreamConfig
    cache: ResolverCacheConfig
    security: ResolverSecurityConfig

class LoggingConfig(BaseModel):
    level: str = Field(..., pattern="^(debug|info|warn|error)$", description="Logging level")
    stdout_log_file: str = Field(..., description="Path to stdout log file")
    stderr_log_file: str = Field(..., description="Path to stderr log file")

class MetricsExporterConfig(BaseModel):
    listen_address: str

class MetricsConfig(BaseModel):
    enabled: bool
    exporter: MetricsExporterConfig

class ConfigSchema(BaseModel):
    server: DNSConfig
    doh: DoHConfig
    resolver: ResolverConfig
    logging: LoggingConfig
    metrics: MetricsConfig
