#!/usr/bin/env sh
set -e

if [ -f .env ]; then
  echo "Loading environment from .env"
  export $(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env | sed 's/^export //')
fi

exec "$@"
