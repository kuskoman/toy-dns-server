#!/usr/bin/env bash

set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

ensure_certs() {
  if [[ ! -f "$script_dir/../certs/localhost.crt" ]]; then
    >&2 echo "[*] Certificates not found, generating..."
    source "$script_dir/generate_certs.sh"
  fi
}

config_file_path="$script_dir/fixtures/config.https.yml"

echo "Starting DNS server with HTTPS..."
set -x
python3 "$script_dir/../toy_dns_server/main.py" --config "$config_file_path"
