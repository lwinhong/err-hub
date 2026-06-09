<template>
  <div class="error-detail">
    <div class="page-header">
      <el-breadcrumb separator="/" class="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/projects' }">{{ t('errorDetail.projectList') }}</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: `/projects/${error.project_id}/errors` }">{{ t('errorDetail.errorList') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ t('errorDetail.errorDetail') }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <el-card shadow="hover" class="info-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">{{ t('errorDetail.errorInfo') }}</span>
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            {{ t('errorDetail.back') }}
          </el-button>
        </div>
      </template>
      <el-descriptions :column="isMobile ? 1 : 2" border>
        <el-descriptions-item :label="t('errorDetail.exceptionType')" :span="2">
          <code class="code-text">{{ error.exception_type }}</code>
        </el-descriptions-item>
        <el-descriptions-item :label="t('errorDetail.message')" :span="2">
          <span class="message-text" :class="{ 'message-code': isCodeLike(error.message) }">{{ error.message }}</span>
        </el-descriptions-item>
        <el-descriptions-item :label="t('errorDetail.severity')">
          <el-tag :type="severityType(error.severity)" :effect="error.severity === 'critical' ? 'dark' : 'light'" size="small">
            {{ error.severity }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="t('errorDetail.environment')">{{ error.environment }}</el-descriptions-item>
        <el-descriptions-item :label="t('errorDetail.source')">
          <el-tag :type="error.source === 'frontend' ? 'warning' : 'primary'" size="small" effect="plain">
            {{ sourceLabel(error.source) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="t('errorDetail.status')">
          <el-tag :type="statusType(error.status)" size="small">{{ statusLabel(error.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="t('errorDetail.ipAddress')">{{ error.ip_address || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="t('errorDetail.count')">{{ error.count }}</el-descriptions-item>
        <el-descriptions-item :label="t('errorDetail.firstSeen')">{{ formatTime(error.first_seen_at) }}</el-descriptions-item>
        <el-descriptions-item :label="t('errorDetail.lastSeen')">{{ formatTime(error.last_seen_at) }}</el-descriptions-item>
      </el-descriptions>

      <div v-if="authStore.isAdmin" class="action-bar">
        <el-button-group>
          <el-button :type="error.status === 'unresolved' ? 'danger' : ''" @click="changeStatus('unresolved')">
            {{ t('errorDetail.markUnresolved') }}
          </el-button>
          <el-button :type="error.status === 'resolved' ? 'success' : ''" @click="changeStatus('resolved')">
            {{ t('errorDetail.markResolved') }}
          </el-button>
          <el-button :type="error.status === 'ignored' ? 'info' : ''" @click="changeStatus('ignored')">
            {{ t('errorDetail.markIgnored') }}
          </el-button>
        </el-button-group>
      </div>
    </el-card>

    <el-card shadow="hover" class="stack-card">
      <template #header>
        <span class="card-title">{{ t('errorDetail.stackTrace') }}</span>
      </template>
      <pre class="stack-trace">{{ error.stack_trace || t('errorDetail.noStackTrace') }}</pre>
    </el-card>

    <el-card shadow="hover" class="context-card">
      <template #header>
        <span class="card-title">{{ t('errorDetail.context') }}</span>
      </template>
      <pre class="context-data">{{ formatContext(error.context) }}</pre>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { getError, updateError } from '../api/errors'
import { formatTime } from '../utils/format'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()
const errorId = route.params.id

const error = ref({})

const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value < 768)

const onResize = () => { windowWidth.value = window.innerWidth }
onMounted(() => { window.addEventListener('resize', onResize); fetchError() })
onUnmounted(() => { window.removeEventListener('resize', onResize) })

const severityType = (severity) => {
  const map = { debug: 'info', warning: 'warning', error: 'danger', critical: 'danger' }
  return map[severity] || 'info'
}

const statusType = (status) => {
  const map = { unresolved: 'danger', resolved: 'success', ignored: 'info' }
  return map[status] || 'info'
}

const statusLabel = (status) => {
  const map = { unresolved: t('errorDetail.unresolved'), resolved: t('errorDetail.resolved'), ignored: t('errorDetail.ignored') }
  return map[status] || status
}

const sourceLabel = (source) => {
  const map = { frontend: t('errorDetail.frontend'), backend: t('errorDetail.backend') }
  return map[source] || source
}

const isCodeLike = (text) => {
  if (!text) return false
  // 包含技术特征的内容视为代码风格
  return /[{}\[\]<>]/.test(text) || /\b(http|Error|TypeError|undefined|null)\b/i.test(text) || text.length > 80
}


const formatContext = (ctx) => {
  if (!ctx) return t('errorDetail.noContext')
  try {
    if (typeof ctx === 'string') {
      const parsed = JSON.parse(ctx)
      return JSON.stringify(parsed, null, 2)
    }
    return JSON.stringify(ctx, null, 2)
  } catch {
    return typeof ctx === 'string' ? ctx : JSON.stringify(ctx, null, 2)
  }
}

const changeStatus = async (status) => {
  try {
    await updateError(errorId, { status })
    error.value.status = status
    ElMessage.success(t('errorDetail.statusUpdated'))
  } catch (err) {
    ElMessage.error(err.response?.data?.error || t('errorDetail.updateFailed'))
  }
}

const goBack = () => {
  if (error.value.project_id) {
    router.push(`/projects/${error.value.project_id}/errors`)
  } else {
    router.back()
  }
}

const fetchError = async () => {
  try {
    const res = await getError(errorId)
    error.value = res.data
  } catch {}
}
</script>

<style scoped>
.error-detail {
  padding: 20px;
}

.breadcrumb {
  margin-bottom: 0;
}

.page-header {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  min-height: 32px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.exception-type,
.code-text {
  font-family: 'Courier New', Courier, monospace;
  font-weight: 600;
  color: var(--el-text-color-primary);
  background-color: var(--el-fill-color-light);
  padding: 2px 6px;
  border-radius: 3px;
}

.message-text {
  word-break: break-all;
  line-height: 1.6;
}

.message-code {
  font-family: 'Courier New', Courier, monospace;
  background-color: var(--el-color-danger-light-9);
  padding: 2px 6px;
  border-radius: 3px;
  color: var(--el-color-danger);
}

.action-bar {
  margin-top: 20px;
}

.info-card {
  margin-bottom: 20px;
}

.stack-card {
  margin-bottom: 20px;
}

.context-card {
  margin-bottom: 20px;
}

.stack-trace {
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
}

.context-data {
  background-color: var(--el-fill-color-light);
  padding: 16px;
  border-radius: 6px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  color: var(--el-text-color-primary);
}

@media (max-width: 768px) {
  .error-detail {
    padding: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .action-bar :deep(.el-button-group) {
    display: flex;
    flex-wrap: wrap;
  }

  .action-bar :deep(.el-button-group .el-button) {
    flex: 1;
    min-width: 0;
  }

  .stack-trace,
  .context-data {
    font-size: 12px;
    padding: 12px;
  }
}
</style>
