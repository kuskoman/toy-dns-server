#!/usr/bin/env bash

set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

check_certs() {
  if [[ ! -f "$script_dir/../certs/localhost.crt" ]]; then
    echo "[-] Certificate not found. Please run scripts/generate_certs.sh first."
    exit 1
  fi
}

if ! check_certs; then
  source "$script_dir/generate_certs.sh"
fi

config_file_path="$script_dir/../fixtures/config.https.yml"

python3 "$script_dir/../toy_dns_server/main.py" --config "$config_file_path"
