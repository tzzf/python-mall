#!/bin/bash
# 用法: ./alembic.sh revision --autogenerate -m "描述"
#       ./alembic.sh upgrade head
#       ./alembic.sh current

cd "$(dirname "$0")"
docker-compose exec backend alembic "$@"
