const API_TOKEN = "your-project-api-token";
const BASE_URL = "http://localhost:5000/api/v1";

async function reportError(exceptionType, message, options = {}) {
  const resp = await fetch(`${BASE_URL}/errors`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Token": API_TOKEN,
    },
    body: JSON.stringify({
      exception_type: exceptionType,
      message: message,
      stack_trace: options.stackTrace || undefined,
      severity: options.severity || "error",
      environment: options.environment || "unknown",
      context: options.context || undefined,
    }),
  });
  return resp.json();
}

// 最简调用
const result1 = await reportError("ValueError", "invalid input data");
console.log(result1);

// 完整调用
const result2 = await reportError(
  "ConnectionError",
  "database connection timeout after 30s",
  {
    stackTrace:
      "Traceback (most recent call last):\n" +
      '  File "/app/db/pool.py", line 22, in get_connection\n' +
      "    conn = pool.acquire(timeout=30)\n" +
      '  File "/app/db/pool.py", line 45, in acquire\n' +
      '    raise ConnectionError("database connection timeout after 30s")',
    severity: "critical",
    environment: "production",
    context: { db_host: "pg-master.internal", db_port: 5432, pool_size: 10 },
  }
);
console.log(result2);
