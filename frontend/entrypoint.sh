#!/bin/sh
set -e

# Runtime injection of API base URL into built static assets.
# Built assets contain a placeholder string __API_BASE__ replaced here.

if [ -z "$VITE_API_URL" ]; then
  VITE_API_URL="https://redhat-api.aiben.io"
fi

echo "[entrypoint] Injecting VITE_API_URL=$VITE_API_URL into built assets..."
TARGET_DIR="/usr/share/nginx/html"

grep -Irl "__API_BASE__" "$TARGET_DIR" 2>/dev/null | while read -r file; do
  sed -i "s|__API_BASE__|$VITE_API_URL|g" "$file" || true
done

echo "[entrypoint] Starting nginx"
exec nginx -g 'daemon off;'
