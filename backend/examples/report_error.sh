#!/bin/bash

API_TOKEN="your-project-api-token"
BASE_URL="http://localhost:5000/api/v1"

# 最简上报（只填必填字段）
curl -X POST "${BASE_URL}/errors" \
  -H "X-API-Token: ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "exception_type": "ValueError",
    "message": "invalid input data"
  }'

# 完整上报（含堆栈、级别、环境、上下文）
curl -X POST "${BASE_URL}/errors" \
  -H "X-API-Token: ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "exception_type": "ConnectionError",
    "message": "database connection timeout after 30s",
    "stack_trace": "Traceback (most recent call last):\n  File \"/app/db/pool.py\", line 22, in get_connection\n    conn = pool.acquire(timeout=30)\n  File \"/app/db/pool.py\", line 45, in acquire\n    raise ConnectionError(\"database connection timeout after 30s\")",
    "severity": "critical",
    "environment": "production",
    "context": {
      "db_host": "pg-master.internal",
      "db_port": 5432,
      "pool_size": 10
    }
  }'
