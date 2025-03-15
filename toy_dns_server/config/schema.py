from pydantic import BaseModel, Field, FilePath, IPvAnyAddress, ValidationError
from typing import List

class DNSConfig(BaseModel):
    address: str = Field(..., description="DNS listening address in IP:PORT format")

class DoHConfig(BaseModel):
    mode: str = Field(..., pattern="^(http|https)$", description="Mode: 'http' or 'https'")
    http_listen_address: str = Field(..., description="Listen address for DoH HTTP mode")
    https_listen_address: str = Field(..., description="Listen address for DoH HTTPS mode")
    certificate_file: FilePath = Field(..., description="Path to TLS certificate")
    key_file: FilePath = Field(..., description="Path to TLS private key")

class ResolverConfig(BaseModel):
    upstream_servers: List[IPvAnyAddress] = Field(..., description="List of upstream DNS resolvers")
    timeout_ms: int = Field(..., gt=0, description="Timeout for upstream DNS queries in milliseconds")

class LoggingConfig(BaseModel):
    level: str = Field(..., pattern="^(debug|info|warn|error)$", description="Logging level")
    stdout_log_file: str = Field(..., description="Path to stdout log file")
    stderr_log_file: str = Field(..., description="Path to stderr log file")

class ConfigSchema(BaseModel):
    server: DNSConfig
    doh: DoHConfig
    resolver: ResolverConfig
    logging: LoggingConfig
