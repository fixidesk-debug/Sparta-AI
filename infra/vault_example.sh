#!/usr/bin/env bash
# Example: fetch secrets from HashiCorp Vault (CLI must be authenticated)
# Usage: source infra/vault_example.sh

set -euo pipefail
VAULT_ADDR=${VAULT_ADDR:-https://vault.example.com}
# Assumes VAULT_TOKEN is set in environment via CI or local login
export VAULT_ADDR

get_secret() {
  local path="$1"
  vault kv get -format=json "$path" | jq -r '.data.data | to_entries[] | "export "+.key+"=\""+.value+"\""'
}

# Example usage: source <(get_secret secret/data/sparta/backend)
# This will export environment variables like DATABASE_URL, REDIS_URL, etc.

