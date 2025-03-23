#!/usr/bin/env bash
set -e

CERT_DIR="certs"
KEY_FILE="$CERT_DIR/localhost.key"
CERT_FILE="$CERT_DIR/localhost.crt"

mkdir -p "$CERT_DIR"

echo "[*] Generating private key..."
openssl genrsa -out "$KEY_FILE" 2048

echo "[*] Generating self-signed certificate..."
openssl req -new -x509 -key "$KEY_FILE" -out "$CERT_FILE" -days 3650 -subj "/CN=localhost"

echo "[*] Certificate and key generated:"
echo "  - Key : $KEY_FILE"
echo "  - Cert: $CERT_FILE"
