<template>
  <div class="detail-page">
    <!-- 标题区 -->
    <div class="page-header">
      <button class="back-btn" @click="goBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        {{ t('errorDetail.back') }}
      </button>
      <div class="breadcrumb-row">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/projects' }">{{ t('errorDetail.projectList') }}</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: `/projects/${error.project_id}/errors` }">{{ projectName || t('errorDetail.errorList') }}</el-breadcrumb-item>
          <el-breadcrumb-item>{{ t('errorDetail.errorDetail') }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
    </div>

    <!-- 错误标题 -->
    <div class="error-hero">
      <div class="hero-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      </div>
      <div class="hero-content">
        <div class="hero-type-row">
          <code class="hero-type">{{ error.exception_type }}</code>
          <span class="sev-badge" :class="'sev-' + error.severity">{{ error.severity }}</span>
          <span class="src-badge" :class="'src-' + error.source">{{ sourceLabel(error.source) }}</span>
          <span class="status-badge" :class="'st-' + error.status">{{ statusLabel(error.status) }}</span>
        </div>
        <p class="hero-message">{{ error.message }}</p>
        <div class="hero-meta">
          <span class="meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
            {{ error.ip_address || '-' }}
          </span>
          <span class="meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            {{ error.environment }}
          </span>
          <span class="meta-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            {{ formatTime(error.last_seen_at) }}
          </span>
          <span class="meta-item count-meta">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            {{ t('errorDetail.count') }}: <strong>{{ error.count }}</strong>
          </span>
        </div>
      </div>
    </div>

    <!-- 状态操作 -->
    <div v-if="authStore.isAdmin" class="status-bar">
      <span class="status-label">{{ t('errorDetail.status') }}</span>
      <div class="status-actions">
        <button
          class="status-btn"
          :class="{ active: error.status === 'unresolved', 'btn-danger': error.status === 'unresolved' }"
          @click="changeStatus('unresolved')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          {{ t('errorDetail.markUnresolved') }}
        </button>
        <button
          class="status-btn"
          :class="{ active: error.status === 'resolved', 'btn-success': error.status === 'resolved' }"
          @click="changeStatus('resolved')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          {{ t('errorDetail.markResolved') }}
        </button>
        <button
          class="status-btn"
          :class="{ active: error.status === 'ignored', 'btn-info': error.status === 'ignored' }"
          @click="changeStatus('ignored')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
          {{ t('errorDetail.markIgnored') }}
        </button>
      </div>
    </div>

    <!-- 信息网格 -->
    <div class="info-grid">
      <div class="info-card">
        <div class="info-icon icon-env">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        </div>
        <div class="info-data">
          <span class="info-value">{{ error.environment || '-' }}</span>
          <span class="info-label">{{ t('errorDetail.environment') }}</span>
        </div>
      </div>
      <div class="info-card">
        <div class="info-icon icon-ip">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
        </div>
        <div class="info-data">
          <span class="info-value">{{ error.ip_address || '-' }}</span>
          <span class="info-label">{{ t('errorDetail.ipAddress') }}</span>
        </div>
      </div>
      <div class="info-card">
        <div class="info-icon icon-count">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        </div>
        <div class="info-data">
          <span class="info-value">{{ error.count }}</span>
          <span class="info-label">{{ t('errorDetail.count') }}</span>
        </div>
      </div>
      <div class="info-card">
        <div class="info-icon icon-first">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <div class="info-data">
          <span class="info-value">{{ formatTime(error.first_seen_at) }}</span>
          <span class="info-label">{{ t('errorDetail.firstSeen') }}</span>
        </div>
      </div>
      <div class="info-card">
        <div class="info-icon icon-last">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <div class="info-data">
          <span class="info-value">{{ formatTime(error.last_seen_at) }}</span>
          <span class="info-label">{{ t('errorDetail.lastSeen') }}</span>
        </div>
      </div>
    </div>

    <!-- 堆栈信息 -->
    <div class="section-card">
      <div class="section-header">
        <div class="section-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
        </div>
        <h3 class="section-title">{{ t('errorDetail.stackTrace') }}</h3>
        <button v-if="error.stack_trace" class="copy-btn" @click="copyText(error.stack_trace)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
        </button>
      </div>
      <div class="stack-scroll-wrap">
        <pre class="code-block">{{ error.stack_trace || t('errorDetail.noStackTrace') }}</pre>
      </div>
    </div>

    <!-- 上下文信息 -->
    <div class="section-card">
      <div class="section-header">
        <div class="section-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
        </div>
        <h3 class="section-title">{{ t('errorDetail.context') }}</h3>
        <button v-if="error.context" class="copy-btn" @click="copyText(formatContext(error.context))">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
        </button>
      </div>
      <pre class="code-block code-light">{{ formatContext(error.context) }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useClipboard } from '@vueuse/core'
import { ElMessage } from 'element-plus'
import { getError, updateError } from '../api/errors'
import { getProject } from '../api/projects'
import { formatTime } from '../utils/format'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()
const { copy: clipboardCopy } = useClipboard({ legacy: true })
const errorId = route.params.id

const error = ref({})
const projectName = ref('')

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

const copyText = async (text) => {
  try {
    await clipboardCopy(text)
    ElMessage.success(t('projects.codeCopied'))
  } catch {
    ElMessage.error(t('projects.copyFailed'))
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
    if (res.data.project_id) {
      try {
        const projRes = await getProject(res.data.project_id)
        projectName.value = projRes.data.name
      } catch { }
    }
  } catch { }
}
</script>

<style scoped>
.detail-page {
  height: 100%;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ── 标题区 ── */
.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  border: 1px solid var(--el-border-color-lighter);
  background: var(--el-bg-color);
  color: var(--el-text-color-regular);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.back-btn:hover {
  border-color: var(--el-border-color);
  color: var(--el-color-primary);
  background: rgba(var(--el-color-primary-rgb), 0.04);
}

/* ── 错误英雄区 ── */
.error-hero {
  display: flex;
  gap: 20px;
  padding: 24px;
  border-radius: 16px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  flex-shrink: 0;
}

.hero-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #ef4444, #f87171);
  color: #fff;
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.35);
  flex-shrink: 0;
}

.hero-icon svg {
  width: 28px;
  height: 28px;
}

.hero-content {
  flex: 1;
  min-width: 0;
}

.hero-type-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.hero-type {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 18px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  background: var(--el-fill-color-light);
  padding: 4px 12px;
  border-radius: 8px;
}

.hero-message {
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
  margin: 0 0 14px;
  word-break: break-all;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.count-meta strong {
  color: var(--el-color-primary);
  font-weight: 700;
}

/* ── 标签 ── */
.sev-badge, .src-badge, .status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 6px;
}

.sev-debug { background: rgba(99, 102, 241, 0.1); color: #6366f1; }
.sev-warning { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.sev-error { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.sev-critical { background: #ef4444; color: #fff; }

.src-frontend { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.src-backend { background: rgba(99, 102, 241, 0.1); color: #6366f1; }

.st-unresolved { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.st-resolved { background: rgba(34, 197, 94, 0.1); color: #22c55e; }
.st-ignored { background: var(--el-fill-color); color: var(--el-text-color-secondary); }

/* ── 状态操作栏 ── */
.status-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 14px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  flex-shrink: 0;
}

.status-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  flex-shrink: 0;
}

.status-actions {
  display: flex;
  gap: 8px;
}

.status-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  border: 2px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-blank);
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-regular);
  cursor: pointer;
  transition: all 0.2s;
}

.status-btn:hover {
  border-color: var(--el-border-color);
}

.status-btn.active.btn-danger {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.06);
  color: #ef4444;
  box-shadow: 0 2px 12px rgba(239, 68, 68, 0.15);
}

.status-btn.active.btn-success {
  border-color: #22c55e;
  background: rgba(34, 197, 94, 0.06);
  color: #22c55e;
  box-shadow: 0 2px 12px rgba(34, 197, 94, 0.15);
}

.status-btn.active.btn-info {
  border-color: var(--el-color-info);
  background: rgba(var(--el-color-info-rgb), 0.06);
  color: var(--el-color-info);
  box-shadow: 0 2px 12px rgba(var(--el-color-info-rgb), 0.15);
}

/* ── 信息网格 ── */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 14px;
  flex-shrink: 0;
}

.info-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  transition: box-shadow 0.3s, border-color 0.3s;
}

.info-card:hover {
  border-color: var(--el-border-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.info-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.info-icon svg {
  width: 18px;
  height: 18px;
}

.icon-env { background: rgba(99, 102, 241, 0.1); color: #6366f1; }
.icon-ip { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.icon-count { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.icon-first { background: rgba(34, 197, 94, 0.1); color: #22c55e; }
.icon-last { background: rgba(168, 85, 247, 0.1); color: #a855f7; }

.info-data {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.info-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* ── 区块卡片 ── */
.section-card {
  border-radius: 14px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
}

.section-card > :last-child {
  border-bottom-left-radius: 13px;
  border-bottom-right-radius: 13px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.section-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-fill-color);
  color: var(--el-text-color-secondary);
}

.section-icon svg {
  width: 16px;
  height: 16px;
}

.section-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  flex: 1;
}

.copy-btn {
  width: 30px;
  height: 30px;
  border-radius: 8px;
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

/* ── 代码块 ── */
.code-block {
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 20px;
  margin: 0;
  font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.7;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.stack-scroll-wrap {
  max-height: 500px;
  overflow-y: auto;
}

.code-light {
  background-color: var(--el-fill-color-light);
  color: var(--el-text-color-primary);
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .detail-page {
    padding: 16px;
    gap: 16px;
  }

  .error-hero {
    flex-direction: column;
    padding: 20px;
  }

  .hero-icon {
    width: 48px;
    height: 48px;
  }

  .hero-icon svg {
    width: 24px;
    height: 24px;
  }

  .hero-type {
    font-size: 16px;
  }

  .hero-meta {
    gap: 12px;
  }

  .status-bar {
    flex-direction: column;
    align-items: flex-start;
  }

  .status-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .status-btn {
    flex: 1;
    min-width: 0;
    justify-content: center;
  }

  .info-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
