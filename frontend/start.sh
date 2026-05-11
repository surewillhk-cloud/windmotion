#!/bin/sh
# frontend/start.sh — Railway 启动脚本
# 将 nginx.conf.template 中的 ${BACKEND_URL} 替换为实际环境变量，然后启动 nginx

set -e

BACKEND_URL="${BACKEND_URL:-http://localhost:8080}"

echo "[start.sh] BACKEND_URL = $BACKEND_URL"

# 用 envsubst 生成最终 nginx 配置
envsubst '${BACKEND_URL}' < /app/nginx.conf.template > /etc/nginx/conf.d/default.conf

echo "[start.sh] nginx config generated:"
cat /etc/nginx/conf.d/default.conf | head -20

# 启动 nginx（前台模式）
exec nginx -g "daemon off;"
