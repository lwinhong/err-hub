<template>
  <div class="p-5 h-full flex flex-col overflow-hidden box-border max-sm:p-3">
    <div class="flex justify-between items-center mb-5 shrink-0 max-sm:flex-col max-sm:items-start max-sm:gap-3">
      <h2 class="m-0 text-xl" style="color: var(--el-text-color-primary)">{{ t('projects.title') }}</h2>
      <el-button v-if="authStore.isAdmin" type="primary" @click="openDialog()">
        <el-icon>
          <Plus />
        </el-icon>
        {{ t('projects.create') }}
      </el-button>
    </div>

    <el-card shadow="hover" class="flex-1 min-h-0 flex flex-col" body-class="flex-1 min-h-0 flex flex-col">
      <div class="flex-1 min-h-0 overflow-hidden">
        <el-table :data="projects" stripe v-loading="loading" height="100%">
          <el-table-column prop="name" :label="t('projects.name')" min-width="150" />
          <el-table-column prop="project_key" :label="t('projects.projectKey')" width="250" />
          <el-table-column :label="t('projects.apiToken')" width="200">
            <template #default="{ row }">
              <div v-if="authStore.isAdmin" class="flex items-center gap-1">
                <span class="font-mono text-[13px]" style="color: var(--el-text-color-regular)">{{
                  maskToken(row.api_token) }}</span>
                <el-button link type="primary" @click="copyToken(row.api_token)">
                  <el-icon>
                    <CopyDocument />
                  </el-icon>
                </el-button>
              </div>
              <span v-else class="font-mono text-[13px]" style="color: var(--el-text-color-regular)">***</span>
            </template>
          </el-table-column>
          <el-table-column prop="description" :label="t('projects.description')" min-width="200"
            show-overflow-tooltip />
          <el-table-column :label="t('projects.errorCount')" width="120" align="center">
            <template #default="{ row }">
              <el-button link type="primary" @click="goToErrors(row)">{{ row.error_count ?? 0 }}</el-button>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" :label="t('projects.createdAt')" width="180">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column :label="t('projects.actions')" :width="authStore.isAdmin ? 390 : 160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="goToErrors(row)">{{ t('projects.viewErrors') }}</el-button>
              <el-button link type="success" @click="openExampleDialog(row)">{{ t('projects.usageExample')
                }}</el-button>
              <template v-if="authStore.isAdmin">
                <el-button link type="primary" @click="openDialog(row)">{{ t('projects.edit') }}</el-button>
                <el-button link type="warning" @click="handleRegenerate(row)">{{ t('projects.regenerateToken')
                  }}</el-button>
                <el-button link type="danger" @click="handleDelete(row)">{{ t('projects.delete') }}</el-button>
              </template>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div
        class="flex justify-end mt-4 shrink-0 max-sm:justify-center max-sm:[&_.el-pagination]:flex-wrap max-sm:[&_.el-pagination]:justify-center">
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total"
          :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @size-change="fetchProjects"
          @current-change="fetchProjects" />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingProject ? t('projects.editProject') : t('projects.createProject')"
      width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item :label="t('projects.projectName')" prop="name">
          <el-input v-model="form.name" :placeholder="t('projects.projectNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('projects.projectDesc')" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3"
            :placeholder="t('projects.projectDescPlaceholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('projects.cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">{{ t('projects.confirm') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="exampleDialogVisible" :title="t('projects.exampleTitle', { name: exampleProjectName })"
      width="920px" destroy-on-close>
      <el-alert :title="t('projects.exampleAlert')" type="info" :closable="false" show-icon
        style="margin-bottom: 16px" />

      <el-tabs>
        <el-tab-pane label="cURL">
          <div class="relative">
            <el-button class="absolute top-2 right-2 z-1" link type="primary" @click="copyCode(curlExample)">
              <el-icon>
                <CopyDocument />
              </el-icon> {{ t('projects.copy') }}
            </el-button>
            <pre class="code-block">{{ curlExample }}</pre>
          </div>
        </el-tab-pane>
        <el-tab-pane label="Python">
          <div class="relative">
            <el-button class="absolute top-2 right-2 z-1" link type="primary" @click="copyCode(pythonExample)">
              <el-icon>
                <CopyDocument />
              </el-icon> {{ t('projects.copy') }}
            </el-button>
            <pre class="code-block">{{ pythonExample }}</pre>
          </div>
        </el-tab-pane>
        <el-tab-pane label="JavaScript">
          <div class="relative">
            <el-button class="absolute top-2 right-2 z-1" link type="primary" @click="copyCode(jsExample)">
              <el-icon>
                <CopyDocument />
              </el-icon> {{ t('projects.copy') }}
            </el-button>
            <pre class="code-block">{{ jsExample }}</pre>
          </div>
        </el-tab-pane>
        <el-tab-pane label="Web SDK">
          <el-alert :title="t('projects.sdkAlert')" type="success" :closable="false" show-icon
            style="margin-bottom: 12px" />
          <div class="relative">
            <el-button class="absolute top-2 right-2 z-1" link type="primary" @click="copyCode(sdkExample)">
              <el-icon>
                <CopyDocument />
              </el-icon> {{ t('projects.copy') }}
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
            <el-tag :type="row.required ? 'danger' : 'info'" size="small">{{ row.required ? t('projects.yes') :
              t('projects.no') }}</el-tag>
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
import { Plus, CopyDocument } from '@element-plus/icons-vue'
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
