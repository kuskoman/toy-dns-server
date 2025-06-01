# Toy DNS Server

A lightweight DNS and DNS-over-HTTPS (DoH) server implementation in Python. This project provides both standard DNS resolution via UDP/TCP and secure DNS-over-HTTPS functionality.

## Features

- **Standard DNS Server**: Handles DNS queries over UDP
- **DNS-over-HTTPS (DoH)**: Supports both HTTP and HTTPS modes
- **DNSSEC Validation**: Optional DNSSEC validation for enhanced security
- **Caching**: Configurable DNS response caching
- **Metrics Export**: Prometheus-compatible metrics endpoint
- **Configurable Upstream Resolvers**: Use your preferred DNS providers

## Prerequisites

- Python 3.8+
- Required packages (see `requirements.txt`)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/toy-dns-server.git
   cd toy-dns-server
   ```

2. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Local Setup

The server can be run directly from the project directory:

```bash
python toy_dns_server/main.py
```

By default, it will use the configuration in `config/config.default.yml`. You can specify a custom configuration file using the `--config` flag:

```bash
python toy_dns_server/main.py --config /path/to/your/config.yml
```

## Configuration

The server uses a YAML-based configuration system with two main files:

1. `config/config.default.yml` - Default settings (should not be modified)
2. `config/config.example.yml` - Example user configuration (copy and modify this)

To customize your configuration, create a copy of `config.example.yml` as `config.yml` and modify as needed.

### Configuration Loading

The configuration system works as follows:

1. The default configuration (`config.default.yml`) is loaded first
2. User configuration is loaded and merged with the default values
3. Command line arguments can override certain configuration options

This layered approach allows for flexibility while maintaining sensible defaults.

### Configuration Structure

The configuration is divided into several sections:

#### Server Configuration

```yaml
server:
  dns:
    # Enable or disable the DNS server
    enabled: true
    # Address where the DNS server listens for UDP/TCP queries
    address: "0.0.0.0:53"

  doh:
    # Enable or disable DNS-over-HTTPS
    enabled: true
    # Mode: "http" or "https"
    mode: "http"

    http:
      # Address for HTTP mode
      listen_address: "127.0.0.1:8053"

    https:
      # Address for HTTPS mode
      listen_address: "0.0.0.0:443"
      security:
        certificate_file: "/path/to/cert.pem"
        key_file: "/path/to/key.pem"
        min_tls_version: "TLS12"
        max_tls_version: "TLS13"
```

#### Resolver Configuration

```yaml
resolver:
  upstream:
    # List of upstream DNS servers
    servers:
      - "8.8.8.8"
      - "1.1.1.1"
      - "9.9.9.9"
    # Timeout in milliseconds
    timeout_ms: 2000

  cache:
    # Enable or disable caching
    enabled: true
    # TTL in seconds ("auto" uses upstream TTL)
    ttl_seconds: auto
    # Maximum cache entries
    max_entries: 1000

  security:
    # Enable DNSSEC validation
    dnssec_validation: true
```

#### Logging Configuration

```yaml
logging:
  # Log level: "debug", "info", "warn", "error"
  level: "info"
  # Log file paths
  stdout_log_file: "stdout"
  stderr_log_file: "stderr"
  # Log format
  log_format: "[%(asctime)s] [PID: %(process)d] [%(logger_name)s] [%(levelname)s] %(message)s"
  # Date format
  date_format: "%Y-%m-%d %H:%M:%S"
```

#### Metrics Configuration

```yaml
metrics:
  # Enable or disable metrics
  enabled: true
  exporter:
    # Address for metrics exporter
    listen_address: "127.0.0.1:9090"
```

## Certificate Generation for HTTPS Testing

When using the HTTPS mode for DoH, you'll need valid TLS certificates. For testing purposes, you can generate self-signed certificates using the included script:

```bash
./scripts/generate_certs.sh
```

This script creates:

- A private key (`scripts/certs/localhost.key`)
- A self-signed certificate (`scripts/certs/localhost.crt`)
- A configuration file (`scripts/certs/localhost.cnf`)

These certificates are configured for `localhost` and `127.0.0.1`, making them suitable for local testing.

## Testing

The project includes several scripts for testing the DNS and DoH functionality:

### Testing Standard DNS

```bash
./scripts/dig_test.sh
```

This script uses the `dig` command to query the DNS server for the A record of `example.com`.

### Testing DoH over HTTP

```bash
./scripts/http_test.py
```

This script sends a DNS query for `example.com` to the DoH server running in HTTP mode.

### Testing DoH over HTTPS

```bash
./scripts/https_test.py
```

This script sends a DNS query to the DoH server running in HTTPS mode, using the self-signed certificate.

### Starting with HTTPS Mode

For convenience, there's a script to start the server in HTTPS mode:

```bash
./scripts/start_with_https.sh
```

This script ensures the certificates exist (generating them if necessary) and starts the server with a configuration that enables HTTPS mode.

## Project Structure

The project is organized into several modules:

### Main Application

- `toy_dns_server/main.py` - Application entry point
- `toy_dns_server/bootstraper.py` - Initializes and coordinates all services

### Server Module

- `toy_dns_server/server/dns/` - Standard DNS server implementation
- `toy_dns_server/server/doh/` - DNS-over-HTTPS implementation
  - Supports both HTTP and HTTPS modes

### Resolver Module

- `toy_dns_server/resolver/dns_resolver.py` - Handles DNS resolution
- `toy_dns_server/security/dnssec.py` - DNSSEC validation

### Cache Module

- `toy_dns_server/cache/cache.py` - DNS response caching

### Configuration Module

- `toy_dns_server/config/loader.py` - Configuration loading
- `toy_dns_server/config/schema.py` - Configuration schema

### Logging Module

- `toy_dns_server/log/` - Logging functionality

### Metrics Module

- `toy_dns_server/metrics/` - Metrics collection and export

## Usage Examples

### Basic Usage

Start the server with default configuration:

```bash
python toy_dns_server/main.py
```

### Custom Configuration

```bash
python toy_dns_server/main.py --config /path/to/config.yml
```

### Using as a Local DNS Resolver

Configure your system to use `127.0.0.1` as the DNS server.

### Using with a Web Browser (DoH)

If running in HTTPS mode with valid certificates, you can configure browsers that support DoH to use:

[https://localhost/](https://localhost/)

## License

See the [LICENSE](LICENSE) file for details.
