#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ADMIN_DIR="$SCRIPT_DIR/admin"
MALL_DIR="$SCRIPT_DIR/mall"

echo "=== 构建前端 ==="
cd "$ADMIN_DIR"
npm install
npm run build

cd "$MALL_DIR"
npm install
npm run build

cd "$SCRIPT_DIR"

echo "=== 启动服务 ==="
docker-compose down
docker-compose -f docker-compose.prod.yml up -d --build

echo "=== 完成 ==="
echo "后台管理: http://localhost:3000"
echo "用户商城:  http://localhost:3001"
echo "API文档:   http://localhost:8000/docs/"
