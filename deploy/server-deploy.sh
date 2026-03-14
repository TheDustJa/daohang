#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${1:-/opt/nav-stack}"
BUNDLE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATA_DIR="/home/daohang/data"

mkdir -p "$APP_DIR"
mkdir -p "$DATA_DIR"

cp "$SCRIPT_DIR/compose.prod.yml" "$APP_DIR/docker-compose.yml"

if [ ! -f "$APP_DIR/.env" ]; then
  cp "$SCRIPT_DIR/.env.prod.example" "$APP_DIR/.env"
fi

docker load -i "$BUNDLE_ROOT/images/nav-backend-release.tar"
docker load -i "$BUNDLE_ROOT/images/nav-frontend-release.tar"

cd "$APP_DIR"
docker compose --env-file .env up -d

echo "Deployment completed."
APP_PORT="$(grep '^APP_PORT=' .env | cut -d '=' -f2)"
APP_PORT="${APP_PORT:-18080}"
echo "Open: http://$(hostname -I | awk '{print $1}'):${APP_PORT}"
echo "DB Path: ${DATA_DIR}/navigation.db"
