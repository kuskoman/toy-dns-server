#!/usr/bin/env bash
set -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)
CERT_DIR="$SCRIPT_DIR/certs"
KEY_FILE="$CERT_DIR/localhost.key"
CERT_FILE="$CERT_DIR/localhost.crt"
CONFIG_FILE="$CERT_DIR/localhost.cnf"

mkdir -p "$CERT_DIR"

cat > "$CONFIG_FILE" <<EOF
[req]
default_bits       = 2048
prompt             = no
default_md         = sha256
x509_extensions    = v3_req
distinguished_name = dn

[dn]
CN = localhost

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
IP.1  = 127.0.0.1
EOF

echo "[*] Generating private key..."
openssl genrsa -out "$KEY_FILE" 2048

echo "[*] Generating self-signed certificate with SAN..."
openssl req -new -x509 \
  -key "$KEY_FILE" \
  -out "$CERT_FILE" \
  -days 3650 \
  -config "$CONFIG_FILE"

echo "[*] Certificate and key generated:"
echo "  - Key : $KEY_FILE"
echo "  - Cert: $CERT_FILE"
echo "  - Config: $CONFIG_FILE"
