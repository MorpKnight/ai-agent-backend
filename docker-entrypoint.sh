#!/usr/bin/env sh
set -e

# If a .env file exists in the working directory, export its variables
if [ -f .env ]; then
  echo "Loading environment from .env"
  # Export lines that look like KEY=VALUE and ignore comments/blank lines
  export $(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env | sed 's/^export //')
fi

exec "$@"
