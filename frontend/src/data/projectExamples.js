export const getFieldDocs = (t) => [
  { field: 'exception_type', required: true, default: '-', desc: t('projects.fieldDocs.exceptionType') },
  { field: 'message', required: true, default: '-', desc: t('projects.fieldDocs.exceptionMessage') },
  { field: 'stack_trace', required: false, default: '-', desc: t('projects.fieldDocs.stackTrace') },
  { field: 'severity', required: false, default: 'error', desc: t('projects.fieldDocs.severity') },
  { field: 'environment', required: false, default: 'unknown', desc: t('projects.fieldDocs.environment') },
  { field: 'context', required: false, default: '-', desc: t('projects.fieldDocs.context') },
]

export const getCurlExample = (token, baseUrl) => `# 最简上报（只填必填字段）
curl -X POST ${baseUrl}/errors \\
  -H "X-API-Token: ${token}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "exception_type": "ValueError",
    "message": "invalid input data"
  }'

# 完整上报（含堆栈、级别、环境、上下文）
curl -X POST ${baseUrl}/errors \\
  -H "X-API-Token: ${token}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "exception_type": "ConnectionError",
    "message": "database connection timeout after 30s",
    "stack_trace": "Traceback (most recent call last):\\n  File \\"/app/db/pool.py\\", line 22, in get_connection\\n    conn = pool.acquire(timeout=30)\\n  File \"/app/db/pool.py\", line 45, in acquire\\n    raise ConnectionError(\\"database connection timeout after 30s\\")",
    "severity": "critical",
    "environment": "production",
    "context": {
      "db_host": "pg-master.internal",
      "db_port": 5432,
      "pool_size": 10
    }
  }'`

export const getPythonExample = (token, baseUrl) => `import requests

API_TOKEN = "${token}"
BASE_URL = "${baseUrl}"


def report_error(exception_type, message, stack_trace=None,
                 severity="error", environment="unknown", context=None):
    resp = requests.post(
        f"{BASE_URL}/errors",
        headers={"X-API-Token": API_TOKEN},
        json={
            "exception_type": exception_type,
            "message": message,
            "stack_trace": stack_trace,
            "severity": severity,
            "environment": environment,
            "context": context,
        },
    )
    return resp.json()


# 最简调用
result = report_error("ValueError", "invalid input data")
print(result)

# 完整调用
result = report_error(
    exception_type="ConnectionError",
    message="database connection timeout after 30s",
    stack_trace=(
        "Traceback (most recent call last):\\n"
        '  File "/app/db/pool.py", line 22, in get_connection\\n'
        "    conn = pool.acquire(timeout=30)\\n"
        '  File "/app/db/pool.py", line 45, in acquire\\n'
        '    raise ConnectionError("database connection timeout after 30s")'
    ),
    severity="critical",
    environment="production",
    context={"db_host": "pg-master.internal", "db_port": 5432},
)
print(result)`

export const getJsExample = (token, baseUrl) => `const API_TOKEN = "${token}";
const BASE_URL = "${baseUrl}";

async function reportError(exceptionType, message, options = {}) {
  const resp = await fetch(\`\${BASE_URL}/errors\`, {
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
      "Traceback (most recent call last):\\n" +
      '  File "/app/db/pool.py", line 22, in get_connection\\n' +
      "    conn = pool.acquire(timeout=30)\\n" +
      '  File "/app/db/pool.py", line 45, in acquire\\n' +
      '    raise ConnectionError("database connection timeout after 30s")',
    severity: "critical",
    environment: "production",
    context: { db_host: "pg-master.internal", db_port: 5432, pool_size: 10 },
  }
);
console.log(result2);`

export const getSdkExample = (token, baseUrl) => {
  const sdkUrl = `${baseUrl.replace('/api/v1', '')}/sdk/error-feedback.js`
  const sc = '</' + 'script>'
  return `<!-- 1. 引入 SDK，自动捕获未处理异常 -->
<script src="${sdkUrl}"
        data-api-token="${token}"
        data-auto-capture="true"
        data-environment="production"
        data-before-send="onBeforeErrorSend">
${sc}

<!-- 2. 手动上报（可在任意 JS 中调用） -->
<script>
  // 最简调用：只填必填字段
  ErrHub.report('TypeError', '按钮点击失败');

  // 完整调用：含堆栈、级别、上下文
  ErrHub.report('ConnectionError', '数据库连接超时', {
    severity: 'critical',
    stackTrace: new Error().stack,
    context: { db_host: 'pg-master', db_port: 5432 }
  });

  // 捕获 Error 对象（推荐在 try/catch 中使用）
  try {
    riskyOperation();
  } catch (e) {
    ErrHub.captureException(e, { severity: 'error' });
  }
${sc}

<!-- 3. 上报前回调：对 payload 二次加工或拦截取消 -->
<script>
  // data-before-send 指定的函数必须挂在 window 上
  window.onBeforeErrorSend = function (payload) {
    // 追加自定义字段
    payload.context = payload.context || {};
    payload.context.user_id = currentUser?.id;
    payload.context.app_version = '2.1.0';

    // 返回修改后的 payload 继续上报
    return payload;

    // 不返回（无 return）也会继续上报（使用原始 payload）

    // 只有显式返回 false 才会取消本次上报：
    // if (payload.severity === 'debug') return false;
  };
${sc}

<!-- ============================================ -->
<!-- script 标签属性说明：                         -->
<!--   data-api-token    必填，项目的 API Token    -->
<!--   data-auto-capture 可选，默认 true，自动捕获 -->
<!--                     全局未处理异常和          -->
<!--                     Promise rejection         -->
<!--   data-environment  可选，默认 production     -->
<!--   data-before-send  可选，指定 window 上的    -->
<!--                     回调函数名，上报前触发    -->
<!--                                             -->
<!-- window.ErrHub 方法：                          -->
<!--   .report(type, msg, opts)  手动上报          -->
<!--   .captureException(e)      上报 Error 对象   -->
<!--   .flush()  立即发送队列中所有待上报的错误     -->
<!--                                             -->
<!-- beforeSend 回调规则：                         -->
<!--   返回 payload（可修改后）→ 继续上报          -->
<!--   不返回（无 return）  → 继续上报原始 payload  -->
<!--   返回 false          → 取消本次上报          -->
<!--   抛出异常             → 仍发送原始 payload  -->
<!-- ============================================ -->`
}
