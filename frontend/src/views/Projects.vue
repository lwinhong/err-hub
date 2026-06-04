<template>
  <div class="projects">
    <div class="page-header">
      <h2>项目管理</h2>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        新建项目
      </el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="projects" stripe v-loading="loading">
        <el-table-column prop="name" label="项目名称" min-width="150" />
        <el-table-column prop="project_key" label="Project Key" width="150" />
        <el-table-column label="API Token" width="200">
          <template #default="{ row }">
            <div class="token-cell">
              <span class="token-text">{{ maskToken(row.api_token) }}</span>
              <el-button link type="primary" @click="copyToken(row.api_token)">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goToErrors(row)">查看异常</el-button>
            <el-button link type="success" @click="openExampleDialog(row)">使用示例</el-button>
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="warning" @click="handleRegenerate(row)">重新生成Token</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchProjects"
          @current-change="fetchProjects"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="editingProject ? '编辑项目' : '新建项目'"
      width="500px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入项目描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="exampleDialogVisible"
      :title="`使用示例 - ${exampleProjectName}`"
      width="720px"
      destroy-on-close
    >
      <el-alert
        title="以下示例中的 API Token 和地址已自动填充为当前项目的实际值，可直接复制使用。"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      />

      <el-tabs>
        <el-tab-pane label="cURL">
          <div class="code-block-wrapper">
            <el-button class="copy-btn" link type="primary" @click="copyCode(curlExample)">
              <el-icon><CopyDocument /></el-icon> 复制
            </el-button>
            <pre class="code-block">{{ curlExample }}</pre>
          </div>
        </el-tab-pane>
        <el-tab-pane label="Python">
          <div class="code-block-wrapper">
            <el-button class="copy-btn" link type="primary" @click="copyCode(pythonExample)">
              <el-icon><CopyDocument /></el-icon> 复制
            </el-button>
            <pre class="code-block">{{ pythonExample }}</pre>
          </div>
        </el-tab-pane>
        <el-tab-pane label="JavaScript">
          <div class="code-block-wrapper">
            <el-button class="copy-btn" link type="primary" @click="copyCode(jsExample)">
              <el-icon><CopyDocument /></el-icon> 复制
            </el-button>
            <pre class="code-block">{{ jsExample }}</pre>
          </div>
        </el-tab-pane>
        <el-tab-pane label="Web SDK">
          <el-alert
            title="引入 SDK 后自动捕获未处理异常，并可通过 window.ErrHub 手动上报。无需额外安装任何依赖。"
            type="success"
            :closable="false"
            show-icon
            style="margin-bottom: 12px"
          />
          <div class="code-block-wrapper">
            <el-button class="copy-btn" link type="primary" @click="copyCode(sdkExample)">
              <el-icon><CopyDocument /></el-icon> 复制
            </el-button>
            <pre class="code-block">{{ sdkExample }}</pre>
          </div>
        </el-tab-pane>
      </el-tabs>

      <el-divider content-position="left">字段说明</el-divider>
      <el-table :data="fieldDocs" size="small" border>
        <el-table-column prop="field" label="字段" width="140" />
        <el-table-column prop="required" label="必填" width="60" align="center">
          <template #default="{ row }">
            <el-tag :type="row.required ? 'danger' : 'info'" size="small">{{ row.required ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="default" label="默认值" width="100" />
        <el-table-column prop="desc" label="说明" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProjects, createProject, updateProject, deleteProject, regenerateToken } from '../api/projects'

const router = useRouter()

const loading = ref(false)
const projects = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const dialogVisible = ref(false)
const submitting = ref(false)
const editingProject = ref(null)
const formRef = ref(null)

const exampleDialogVisible = ref(false)
const exampleProjectToken = ref('')
const exampleProjectName = ref('')

const form = reactive({
  name: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }]
}

const fieldDocs = [
  { field: 'exception_type', required: true, default: '-', desc: '异常类型，如 ValueError、KeyError' },
  { field: 'message', required: true, default: '-', desc: '异常消息' },
  { field: 'stack_trace', required: false, default: '-', desc: '完整堆栈信息' },
  { field: 'severity', required: false, default: 'error', desc: 'debug / info / warning / error / critical' },
  { field: 'environment', required: false, default: 'unknown', desc: 'development / staging / production' },
  { field: 'context', required: false, default: '-', desc: '自定义 JSON 对象，如 {"user_id": "123"}' },
]

const baseUrl = `${window.location.origin}/api/v1`

const curlExample = computed(() => {
  const token = exampleProjectToken.value
  return `# 最简上报（只填必填字段）
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
    "stack_trace": "Traceback (most recent call last):\\n  File \\"/app/db/pool.py\\", line 22, in get_connection\\n    conn = pool.acquire(timeout=30)\\n  File \\"/app/db/pool.py\\", line 45, in acquire\\n    raise ConnectionError(\\"database connection timeout after 30s\\")",
    "severity": "critical",
    "environment": "production",
    "context": {
      "db_host": "pg-master.internal",
      "db_port": 5432,
      "pool_size": 10
    }
  }'`
})

const pythonExample = computed(() => {
  const token = exampleProjectToken.value
  return `import requests

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
})

const jsExample = computed(() => {
  const token = exampleProjectToken.value
  return `const API_TOKEN = "${token}";
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
})

const sdkExample = computed(() => {
  const token = exampleProjectToken.value
  const sdkUrl = `${window.location.origin}/sdk/error-feedback.js`
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
})

const maskToken = (token) => {
  if (!token) return '-'
  if (token.length <= 8) return token
  return token.slice(0, 4) + '****' + token.slice(-4)
}

const copyToken = async (token) => {
  try {
    await navigator.clipboard.writeText(token)
    ElMessage.success('Token 已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

const copyCode = async (code) => {
  try {
    await navigator.clipboard.writeText(code)
    ElMessage.success('代码已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

const formatTime = (t) => {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

const goToErrors = (row) => {
  router.push(`/projects/${row.id}/errors`)
}

const openExampleDialog = (row) => {
  exampleProjectToken.value = row.api_token
  exampleProjectName.value = row.name
  exampleDialogVisible.value = true
}

const openDialog = (project = null) => {
  editingProject.value = project
  form.name = project ? project.name : ''
  form.description = project ? project.description : ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (editingProject.value) {
        await updateProject(editingProject.value.id, form)
        ElMessage.success('项目已更新')
      } else {
        await createProject(form)
        ElMessage.success('项目已创建')
      }
      dialogVisible.value = false
      fetchProjects()
    } catch (err) {
      ElMessage.error(err.response?.data?.error || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除项目 "${row.name}" 吗？`, '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteProject(row.id)
      ElMessage.success('项目已删除')
      fetchProjects()
    } catch (err) {
      ElMessage.error(err.response?.data?.error || '删除失败')
    }
  }).catch(() => {})
}

const handleRegenerate = (row) => {
  ElMessageBox.confirm('重新生成 Token 后，旧 Token 将立即失效。确定继续？', '重新生成 Token', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await regenerateToken(row.id)
      ElMessage.success('Token 已重新生成')
      fetchProjects()
    } catch (err) {
      ElMessage.error(err.response?.data?.error || '操作失败')
    }
  }).catch(() => {})
}

const fetchProjects = async () => {
  loading.value = true
  try {
    const res = await getProjects({ page: page.value, per_page: pageSize.value })
    projects.value = res.data.items || res.data
    total.value = res.data.total || projects.value.length
  } catch {} finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
.projects {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.token-cell {
  display: flex;
  align-items: center;
  gap: 4px;
}

.token-text {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  color: #606266;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.code-block-wrapper {
  position: relative;
}

.copy-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 1;
}

.code-block {
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 6px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  max-height: 500px;
  overflow-y: auto;
}
</style>
