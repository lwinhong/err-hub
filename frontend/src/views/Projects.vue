<template>
  <div class="projects-page">
    <!-- 标题区 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon">
          <el-icon :size="28"><FolderOpened /></el-icon>
        </div>
        <div>
          <h2 class="header-title">{{ t('projects.title') }}</h2>
          <p class="header-subtitle">{{ t('projects.subtitle') }}</p>
        </div>
      </div>
      <button v-if="authStore.isAdmin" class="add-btn" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        <span>{{ t('projects.create') }}</span>
      </button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card stat-total">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ total }}</span>
          <span class="stat-label">{{ t('projects.totalProjects') }}</span>
        </div>
      </div>
      <div class="stat-card stat-errors">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ totalErrors }}</span>
          <span class="stat-label">{{ t('projects.totalErrors') }}</span>
        </div>
      </div>
      <div class="stat-card stat-recent">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ recentCount }}</span>
          <span class="stat-label">{{ t('projects.recentProjects') }}</span>
        </div>
      </div>
    </div>

    <!-- 项目列表 -->
    <div class="projects-table-wrap" v-loading="loading">
      <div class="table-header">
        <span class="col-name">{{ t('projects.name') }}</span>
        <span class="col-desc">{{ t('projects.description') }}</span>
        <span class="col-token">{{ t('projects.apiToken') }}</span>
        <span class="col-errors">{{ t('projects.errorCount') }}</span>
        <span class="col-time">{{ t('projects.createdAt') }}</span>
        <span class="col-actions">{{ t('projects.actions') }}</span>
      </div>
      <div v-for="row in projects" :key="row.id" class="table-row">
        <div class="col-name">
          <div class="project-avatar">{{ row.name.charAt(0).toUpperCase() }}</div>
          <span class="project-name">{{ row.name }}</span>
        </div>
        <div class="col-desc">
          <span class="desc-text" :title="row.description">{{ row.description || '-' }}</span>
        </div>
        <div class="col-token">
          <div v-if="authStore.isAdmin" class="token-cell">
            <code class="token-value">{{ maskToken(row.api_token) }}</code>
            <button class="copy-btn" @click="copyToken(row.api_token)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            </button>
          </div>
          <span v-else class="token-masked">***</span>
        </div>
        <div class="col-errors">
          <button class="error-count-btn" @click="goToErrors(row)">
            {{ row.error_count ?? 0 }}
          </button>
        </div>
        <div class="col-time">{{ formatTime(row.created_at) }}</div>
        <div class="col-actions">
          <el-tooltip :content="t('projects.viewErrors')" placement="top" :show-after="300">
            <button class="action-btn action-view" @click="goToErrors(row)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </el-tooltip>
          <el-tooltip :content="t('projects.usageExample')" placement="top" :show-after="300">
            <button class="action-btn action-code" @click="openExampleDialog(row)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
            </button>
          </el-tooltip>
          <template v-if="authStore.isAdmin">
            <el-tooltip :content="t('projects.edit')" placement="top" :show-after="300">
              <button class="action-btn action-edit" @click="openDialog(row)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
              </button>
            </el-tooltip>
            <el-tooltip :content="t('projects.regenerateToken')" placement="top" :show-after="300">
              <button class="action-btn action-refresh" @click="handleRegenerate(row)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
              </button>
            </el-tooltip>
            <el-tooltip :content="t('projects.delete')" placement="top" :show-after="300">
              <button class="action-btn action-delete" @click="handleDelete(row)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
              </button>
            </el-tooltip>
          </template>
        </div>
      </div>
      <div v-if="!loading && projects.length === 0" class="table-empty">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
        <span>{{ t('projects.noData') }}</span>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrap">
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

    <!-- 新建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingProject ? t('projects.editProject') : t('projects.createProject')" width="500px" destroy-on-close class="modern-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="dialog-form">
        <el-form-item :label="t('projects.projectName')" prop="name">
          <el-input v-model="form.name" :placeholder="t('projects.projectNamePlaceholder')" size="large" />
        </el-form-item>
        <el-form-item :label="t('projects.projectDesc')">
          <el-input v-model="form.description" type="textarea" :rows="3" :placeholder="t('projects.projectDescPlaceholder')" size="large" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false" size="large">{{ t('projects.cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit" size="large">{{ t('projects.confirm') }}</el-button>
      </template>
    </el-dialog>

    <!-- 使用示例对话框 -->
    <el-dialog v-model="exampleDialogVisible" :title="t('projects.exampleTitle', { name: exampleProjectName })" width="920px" destroy-on-close class="modern-dialog">
      <el-alert :title="t('projects.exampleAlert')" type="info" :closable="false" show-icon style="margin-bottom: 16px" />
      <el-tabs>
        <el-tab-pane label="cURL">
          <div class="relative">
            <el-button class="absolute top-2 right-2 z-1" link type="primary" @click="copyCode(curlExample)">
              <el-icon><CopyDocument /></el-icon> {{ t('projects.copy') }}
            </el-button>
            <pre class="code-block">{{ curlExample }}</pre>
          </div>
        </el-tab-pane>
        <el-tab-pane label="Python">
          <div class="relative">
            <el-button class="absolute top-2 right-2 z-1" link type="primary" @click="copyCode(pythonExample)">
              <el-icon><CopyDocument /></el-icon> {{ t('projects.copy') }}
            </el-button>
            <pre class="code-block">{{ pythonExample }}</pre>
          </div>
        </el-tab-pane>
        <el-tab-pane label="JavaScript">
          <div class="relative">
            <el-button class="absolute top-2 right-2 z-1" link type="primary" @click="copyCode(jsExample)">
              <el-icon><CopyDocument /></el-icon> {{ t('projects.copy') }}
            </el-button>
            <pre class="code-block">{{ jsExample }}</pre>
          </div>
        </el-tab-pane>
        <el-tab-pane label="Web SDK">
          <el-alert :title="t('projects.sdkAlert')" type="success" :closable="false" show-icon style="margin-bottom: 12px" />
          <div class="relative">
            <el-button class="absolute top-2 right-2 z-1" link type="primary" @click="copyCode(sdkExample)">
              <el-icon><CopyDocument /></el-icon> {{ t('projects.copy') }}
            </el-button>
            <pre class="code-block">{{ sdkExample }}</pre>
          </div>
        </el-tab-pane>
      </el-tabs>
      <el-divider content-position="left">{{ t('projects.fieldDescription') }}</el-divider>
      <el-table :data="fieldDocs" size="small" border>
        <el-table-column prop="field" :label="t('projects.field')" width="140" />
        <el-table-column prop="required" :label="t('projects.required')" width="60" align="center">
          <template #default="{ row }">
            <el-tag :type="row.required ? 'danger' : 'info'" size="small">{{ row.required ? t('projects.yes') : t('projects.no') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="default" :label="t('projects.defaultValue')" width="100" />
        <el-table-column prop="desc" :label="t('projects.explain')" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useClipboard } from '@vueuse/core'
import { Plus, CopyDocument, FolderOpened } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProjects, createProject, updateProject, deleteProject, regenerateToken } from '../api/projects'
import { useAuthStore } from '../stores/auth'
import { useSettingsStore } from '../stores/settings'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()
const settingsStore = useSettingsStore()
const { copy: clipboardCopy } = useClipboard({ legacy: true })

const loading = ref(false)
const projects = ref([])
const page = ref(1)
const pageSize = ref(20)
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
  name: [{ required: true, message: t('projects.nameRequired'), trigger: 'blur' }]
}

const fieldDocs = [
  { field: 'exception_type', required: true, default: '-', desc: t('projects.fieldDocs.exceptionType') },
  { field: 'message', required: true, default: '-', desc: t('projects.fieldDocs.exceptionMessage') },
  { field: 'stack_trace', required: false, default: '-', desc: t('projects.fieldDocs.stackTrace') },
  { field: 'severity', required: false, default: 'error', desc: t('projects.fieldDocs.severity') },
  { field: 'environment', required: false, default: 'unknown', desc: t('projects.fieldDocs.environment') },
  { field: 'context', required: false, default: '-', desc: t('projects.fieldDocs.context') },
]

const baseUrl = `${window.location.origin}/api/v1`

const totalErrors = computed(() => projects.value.reduce((sum, p) => sum + (p.error_count ?? 0), 0))
const recentCount = computed(() => {
  const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000
  return projects.value.filter(p => new Date(p.created_at).getTime() > weekAgo).length
})

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
    "stack_trace": "Traceback (most recent call last):\\n  File \\"/app/db/pool.py\\", line 22, in get_connection\\n    conn = pool.acquire(timeout=30)\\n  File \"/app/db/pool.py\", line 45, in acquire\\n    raise ConnectionError(\\"database connection timeout after 30s\\")",
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
    await clipboardCopy(token)
    ElMessage.success(t('projects.tokenCopied'))
  } catch {
    ElMessage.error(t('projects.copyFailed'))
  }
}

const copyCode = async (code) => {
  try {
    await clipboardCopy(code)
    ElMessage.success(t('projects.codeCopied'))
  } catch {
    ElMessage.error(t('projects.copyFailed'))
  }
}

const formatTime = (t) => {
  if (!t) return '-'
  return new Date(t).toLocaleString(localStorage.getItem('locale') === 'en' ? 'en-US' : 'zh-CN')
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
        ElMessage.success(t('projects.projectUpdated'))
      } else {
        await createProject(form)
        ElMessage.success(t('projects.projectCreated'))
      }
      dialogVisible.value = false
      fetchProjects()
    } catch (err) {
      ElMessage.error(err.response?.data?.error || t('projects.operationFailed'))
    } finally {
      submitting.value = false
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(t('projects.deleteConfirm', { name: row.name }), t('projects.deleteTitle'), {
    confirmButtonText: t('projects.confirm'),
    cancelButtonText: t('projects.cancel'),
    type: 'warning'
  }).then(async () => {
    try {
      await deleteProject(row.id)
      ElMessage.success(t('projects.projectDeleted'))
      fetchProjects()
    } catch (err) {
      ElMessage.error(err.response?.data?.error || t('projects.deleteFailed'))
    }
  }).catch(() => { })
}

const handleRegenerate = (row) => {
  ElMessageBox.confirm(t('projects.regenerateConfirm'), t('projects.regenerateTitle'), {
    confirmButtonText: t('projects.confirm'),
    cancelButtonText: t('projects.cancel'),
    type: 'warning'
  }).then(async () => {
    try {
      await regenerateToken(row.id)
      ElMessage.success(t('projects.tokenRegenerated'))
      fetchProjects()
    } catch (err) {
      ElMessage.error(err.response?.data?.error || t('projects.operationFailed'))
    }
  }).catch(() => { })
}

const fetchProjects = async () => {
  loading.value = true
  try {
    const res = await getProjects({ page: page.value, per_page: pageSize.value })
    projects.value = res.data.items || res.data
    total.value = res.data.total || projects.value.length
  } catch { } finally {
    loading.value = false
  }
}

onMounted(() => {
  pageSize.value = settingsStore.defaultPageSize
  fetchProjects()
})

watch(() => settingsStore.defaultPageSize, (val) => {
  pageSize.value = val
  page.value = 1
  fetchProjects()
})
</script>

<style scoped>
.projects-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 24px;
  gap: 20px;
}

/* ── 标题区 ── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  color: #fff;
  box-shadow: 0 4px 16px rgba(245, 158, 11, 0.35);
}

.header-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.header-subtitle {
  margin: 2px 0 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(245, 158, 11, 0.35);
  transition: all 0.25s;
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(245, 158, 11, 0.45);
}

.add-btn:active {
  transform: translateY(0);
}

/* ── 统计卡片 ── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  flex-shrink: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  border-radius: 14px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  transition: box-shadow 0.3s, border-color 0.3s;
}

.stat-card:hover {
  border-color: var(--el-border-color);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 22px;
  height: 22px;
}

.stat-total .stat-icon {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.stat-errors .stat-icon {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.stat-recent .stat-icon {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  line-height: 1;
  color: var(--el-text-color-primary);
  font-variant-numeric: tabular-nums;
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* ── 表格 ── */
.projects-table-wrap {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  border-radius: 14px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
}

.table-header {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color-lighter);
  font-size: 12px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  position: sticky;
  top: 0;
  z-index: 1;
}

.table-row {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  transition: background 0.15s;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background: var(--el-fill-color-lighter);
}

.col-name {
  flex: 1.5;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.col-desc {
  flex: 1.5;
  min-width: 0;
}

.col-token {
  flex: 1.2;
}

.col-errors {
  flex: 0 0 80px;
  text-align: center;
}

.col-time {
  flex: 1;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.col-actions {
  flex: 0 0 180px;
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: flex-end;
}

/* ── 项目头像 ── */
.project-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  flex-shrink: 0;
}

.project-name {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

/* ── 描述 ── */
.desc-text {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

/* ── Token ── */
.token-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.token-value {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 6px;
  background: var(--el-fill-color);
  color: var(--el-text-color-secondary);
}

.token-masked {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

.copy-btn {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-secondary);
  transition: all 0.2s;
}

.copy-btn:hover {
  background: var(--el-fill-color);
  color: var(--el-color-primary);
}

/* ── 错误数 ── */
.error-count-btn {
  border: none;
  background: transparent;
  font-size: 15px;
  font-weight: 700;
  color: var(--el-color-primary);
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 8px;
  transition: all 0.2s;
  font-variant-numeric: tabular-nums;
}

.error-count-btn:hover {
  background: rgba(var(--el-color-primary-rgb), 0.08);
}

/* ── 操作按钮 ── */
.action-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  color: var(--el-text-color-secondary);
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.action-btn:hover {
  background: var(--el-fill-color);
}

.action-view:hover { color: #3b82f6; }
.action-code:hover { color: #22c55e; }
.action-edit:hover { color: #3b82f6; }
.action-refresh:hover { color: #f59e0b; }
.action-delete:hover { color: #ef4444; background: rgba(239, 68, 68, 0.08); }

/* ── 空状态 ── */
.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px 20px;
  color: var(--el-text-color-placeholder);
}

/* ── 分页 ── */
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}

/* ── 代码块 ── */
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

/* ── 对话框 ── */
.dialog-form :deep(.el-form-item__label) {
  font-weight: 600;
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .projects-page {
    padding: 16px;
    gap: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .add-btn {
    width: 100%;
    justify-content: center;
  }

  .stats-row {
    grid-template-columns: 1fr;
  }

  .col-desc,
  .col-time {
    display: none;
  }

  .col-actions {
    flex: 0 0 140px;
  }

  .table-header,
  .table-row {
    padding: 10px 14px;
  }
}
</style>
