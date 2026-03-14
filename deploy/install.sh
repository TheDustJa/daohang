#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

chmod +x "$BASE_DIR/deploy/server-deploy.sh"
"$BASE_DIR/deploy/server-deploy.sh" /opt/nav-stack
