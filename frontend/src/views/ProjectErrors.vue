<template>
  <div class="errors-page">
    <!-- 标题区 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <el-icon :size="28"><Warning /></el-icon>
        </div>
        <div>
          <div class="breadcrumb-row">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/projects' }">{{ t('projectErrors.breadcrumbProjects') }}</el-breadcrumb-item>
              <el-breadcrumb-item>{{ projectName }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <h2 class="header-title">{{ t('projectErrors.titleSuffix') }}</h2>
        </div>
      </div>
      <div class="header-right">
        <el-select
          :model-value="projectId"
          :placeholder="t('projectErrors.switchProject')"
          style="width: 200px"
          @change="switchProject"
          size="large"
        >
          <el-option v-for="p in projectList" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card stat-total">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ total }}</span>
          <span class="stat-label">{{ t('projectErrors.totalErrors') }}</span>
        </div>
      </div>
      <div class="stat-card stat-critical">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ criticalCount }}</span>
          <span class="stat-label">{{ t('projectErrors.criticalErrors') }}</span>
        </div>
      </div>
      <div class="stat-card stat-unresolved">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ unresolvedCount }}</span>
          <span class="stat-label">{{ t('projectErrors.unresolvedCount') }}</span>
        </div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar" v-loading="loading">
      <div class="filter-row">
        <el-select v-model="filters.severity" :placeholder="t('projectErrors.severity')" clearable multiple collapse-tags collapse-tags-tooltip @change="fetchErrors" class="filter-item">
          <el-option label="Debug" value="debug" />
          <el-option label="Warning" value="warning" />
          <el-option label="Error" value="error" />
          <el-option label="Critical" value="critical" />
        </el-select>
        <el-select v-model="filters.environment" :placeholder="t('projectErrors.environment')" clearable multiple collapse-tags collapse-tags-tooltip @change="fetchErrors" class="filter-item">
          <el-option label="Production" value="production" />
          <el-option label="Staging" value="staging" />
          <el-option label="Development" value="development" />
        </el-select>
        <el-select v-model="filters.source" :placeholder="t('projectErrors.source')" clearable multiple collapse-tags collapse-tags-tooltip @change="fetchErrors" class="filter-item">
          <el-option :label="t('projectErrors.frontend')" value="frontend" />
          <el-option :label="t('projectErrors.backend')" value="backend" />
        </el-select>
        <el-select v-model="filters.status" :placeholder="t('projectErrors.status')" clearable multiple collapse-tags collapse-tags-tooltip @change="fetchErrors" class="filter-item">
          <el-option :label="t('projectErrors.unresolved')" value="unresolved" />
          <el-option :label="t('projectErrors.resolved')" value="resolved" />
          <el-option :label="t('projectErrors.ignored')" value="ignored" />
        </el-select>
        <el-select v-model="filters.sort" :placeholder="t('projectErrors.sort')" @change="fetchErrors" class="filter-item">
          <el-option :label="t('projectErrors.lastSeen')" value="last_seen_at" />
          <el-option :label="t('projectErrors.count')" value="count" />
          <el-option :label="t('projectErrors.firstSeen')" value="first_seen_at" />
        </el-select>
        <div class="search-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-icon"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input
            v-model="filters.search"
            :placeholder="t('projectErrors.searchPlaceholder')"
            class="search-input"
            @keyup.enter="fetchErrors"
          />
          <button v-if="filters.search" class="search-clear" @click="filters.search = ''; fetchErrors()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 错误列表 -->
    <div class="errors-table-wrap" v-loading="loading">
      <div class="table-header">
        <span v-if="authStore.isAdmin" class="col-check">
          <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" class="custom-checkbox" />
        </span>
        <span class="col-type">{{ t('projectErrors.exceptionType') }}</span>
        <span class="col-msg">{{ t('projectErrors.message') }}</span>
        <span v-if="settingsStore.showUserColumn" class="col-user">{{ t('projectErrors.user') }}</span>
        <span class="col-severity">{{ t('projectErrors.severity') }}</span>
        <span class="col-source">{{ t('projectErrors.source') }}</span>
        <span class="col-env">{{ t('projectErrors.environment') }}</span>
        <span class="col-count">{{ t('projectErrors.count') }}</span>
        <span class="col-status">{{ t('projectErrors.status') }}</span>
        <span class="col-time">{{ t('projectErrors.lastSeen') }}</span>
        <span class="col-actions">{{ t('projectErrors.actions') }}</span>
      </div>
      <div v-for="row in errors" :key="row.id" class="table-row" @click="goToError(row)">
        <span v-if="authStore.isAdmin" class="col-check" @click.stop>
          <input type="checkbox" :checked="selectedIds.includes(row.id)" @change="toggleSelect(row)" class="custom-checkbox" />
        </span>
        <div class="col-type">
          <span class="type-badge">{{ row.exception_type }}</span>
        </div>
        <div class="col-msg">
          <span class="msg-text" :title="row.message">{{ row.message }}</span>
        </div>
        <div v-if="settingsStore.showUserColumn" class="col-user">
          <span class="user-text">{{ row.user || '-' }}</span>
        </div>
        <div class="col-severity">
          <span class="sev-badge" :class="'sev-' + row.severity">{{ row.severity }}</span>
        </div>
        <div class="col-source">
          <span class="src-badge" :class="'src-' + row.source">{{ sourceLabel(row.source) }}</span>
        </div>
        <div class="col-env">
          <span class="env-text">{{ row.environment }}</span>
        </div>
        <div class="col-count">
          <span class="count-value">{{ row.count }}</span>
        </div>
        <div class="col-status">
          <span class="status-badge" :class="'st-' + row.status">{{ statusLabel(row.status) }}</span>
        </div>
        <div class="col-time">
          <span class="time-text">{{ formatTime(row.last_seen_at) }}</span>
        </div>
        <div class="col-actions" @click.stop>
          <el-tooltip :content="t('projectErrors.detail')" placement="top" :show-after="300">
            <button class="action-btn action-view" @click="goToError(row)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </el-tooltip>
          <el-tooltip v-if="authStore.isAdmin" :content="t('projectErrors.delete')" placement="top" :show-after="300">
            <button class="action-btn action-delete" @click="handleDelete(row)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            </button>
          </el-tooltip>
        </div>
      </div>
      <div v-if="!loading && errors.length === 0" class="table-empty">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        <span>{{ t('projectErrors.noData') }}</span>
      </div>
    </div>

    <!-- 分页 + 批量删除 -->
    <div class="bottom-bar">
      <transition name="slide-up">
        <div v-if="authStore.isAdmin && selectedIds.length > 0" class="batch-bar">
          <span class="batch-count">{{ t('projectErrors.batchDelete', { count: selectedIds.length }) }}</span>
          <button class="batch-btn" @click="handleBatchDelete">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            {{ t('projectErrors.deleteBtn') }}
          </button>
        </div>
      </transition>
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchErrors"
        @current-change="fetchErrors"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { Warning } from '@element-plus/icons-vue'
import { getProjectErrors, deleteError, batchDeleteErrors } from '../api/errors'
import { getProject, getProjects } from '../api/projects'
import { formatTime } from '../utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { useSettingsStore } from '../stores/settings'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()
const settingsStore = useSettingsStore()
const projectId = computed(() => route.params.id)

const projectName = ref('')
const projectList = ref([])
const loading = ref(false)
const errors = ref([])
const selectedIds = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filters = reactive({
  severity: [],
  environment: [],
  source: [],
  status: ['unresolved'],
  search: '',
  sort: 'last_seen_at'
})

const criticalCount = computed(() => errors.value.filter(e => e.severity === 'critical').length)
const unresolvedCount = computed(() => errors.value.filter(e => e.status === 'unresolved').length)
const isAllSelected = computed(() => errors.value.length > 0 && errors.value.every(e => selectedIds.value.includes(e.id)))

const severityType = (severity) => {
  const map = { debug: 'info', warning: 'warning', error: 'danger', critical: 'danger' }
  return map[severity] || 'info'
}

const statusType = (status) => {
  const map = { unresolved: 'danger', resolved: 'success', ignored: 'info' }
  return map[status] || 'info'
}

const statusLabel = (status) => {
  const map = { unresolved: t('projectErrors.unresolved'), resolved: t('projectErrors.resolved'), ignored: t('projectErrors.ignored') }
  return map[status] || status
}

const sourceLabel = (source) => {
  const map = { frontend: t('projectErrors.frontend'), backend: t('projectErrors.backend') }
  return map[source] || source
}

const goToError = (row) => {
  router.push(`/errors/${row.id}`)
}

const toggleSelect = (row) => {
  const idx = selectedIds.value.indexOf(row.id)
  if (idx === -1) {
    selectedIds.value.push(row.id)
  } else {
    selectedIds.value.splice(idx, 1)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = errors.value.map(e => e.id)
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      t('projectErrors.deleteConfirm', { type: row.exception_type, message: row.message }),
      t('projectErrors.deleteTitle'),
      { confirmButtonText: t('projectErrors.deleteBtn'), cancelButtonText: t('projectErrors.cancel'), type: 'warning' }
    )
    await deleteError(row.id)
    ElMessage.success(t('projectErrors.deleteSuccess'))
    fetchErrors()
  } catch {}
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      t('projectErrors.batchDeleteConfirm', { count: selectedIds.value.length }),
      t('projectErrors.batchDeleteTitle'),
      { confirmButtonText: t('projectErrors.deleteBtn'), cancelButtonText: t('projectErrors.cancel'), type: 'warning' }
    )
    const res = await batchDeleteErrors(selectedIds.value)
    ElMessage.success(t('projectErrors.batchDeleteSuccess', { count: res.data.deleted }))
    selectedIds.value = []
    fetchErrors()
  } catch {}
}

const fetchErrors = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      per_page: pageSize.value
    }
    if (filters.severity.length) params.severity = filters.severity.join(',')
    if (filters.environment.length) params.environment = filters.environment.join(',')
    if (filters.source.length) params.source = filters.source.join(',')
    if (filters.status.length) params.status = filters.status.join(',')
    if (filters.search) params.search = filters.search
    if (filters.sort) params.sort = filters.sort
    const res = await getProjectErrors(projectId.value, params)
    errors.value = res.data.items || res.data
    total.value = res.data.total || errors.value.length
  } catch {} finally {
    loading.value = false
  }
}

const fetchProject = async () => {
  try {
    const res = await getProject(projectId.value)
    projectName.value = res.data.name
  } catch {}
}

const fetchProjects = async () => {
  try {
    const res = await getProjects({ page: 1, per_page: 100 })
    projectList.value = res.data.items || []
  } catch {}
}

const switchProject = (id) => {
  router.push(`/projects/${id}/errors`)
}

watch(() => route.params.id, () => {
  page.value = 1
  fetchProject()
  fetchErrors()
})

watch(() => settingsStore.defaultPageSize, (val) => {
  pageSize.value = val
  page.value = 1
  fetchErrors()
})

onMounted(() => {
  pageSize.value = settingsStore.defaultPageSize
  fetchProjects()
  fetchProject()
  fetchErrors()
})
</script>

<style scoped>
.errors-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 24px;
  gap: 18px;
}

/* ── 标题区 ── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.header-left {
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
  background: linear-gradient(135deg, #ef4444, #f87171);
  color: #fff;
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.35);
}

.breadcrumb-row {
  margin-bottom: 2px;
}

.header-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
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

.stat-total .stat-icon { background: rgba(99, 102, 241, 0.1); color: #6366f1; }
.stat-critical .stat-icon { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.stat-unresolved .stat-icon { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }

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

/* ── 筛选栏 ── */
.filter-bar {
  flex-shrink: 0;
  padding: 16px 20px;
  border-radius: 14px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.filter-item {
  flex: 1 1 140px;
  min-width: 120px;
}

.search-box {
  flex: 2 1 200px;
  min-width: 180px;
  position: relative;
  display: flex;
  align-items: center;
  height: 32px;
  padding: 0 12px;
  border-radius: var(--el-border-radius-base);
  border: 1px solid var(--el-border-color);
  background: var(--el-fill-color-blank);
  transition: border-color 0.2s;
}

.search-box:focus-within {
  border-color: var(--el-color-primary);
}

.search-icon {
  width: 14px;
  height: 14px;
  color: var(--el-text-color-placeholder);
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  color: var(--el-text-color-primary);
  padding: 0 8px;
}

.search-input::placeholder {
  color: var(--el-text-color-placeholder);
}

.search-clear {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: none;
  background: var(--el-fill-color);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-secondary);
  transition: all 0.2s;
}

.search-clear:hover {
  background: var(--el-fill-color-dark);
  color: var(--el-text-color-primary);
}

/* ── 表格 ── */
.errors-table-wrap {
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
  padding: 12px 16px;
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
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  cursor: pointer;
  transition: background 0.15s;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background: var(--el-fill-color-lighter);
}

.col-check {
  flex: 0 0 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.custom-checkbox {
  width: 16px;
  height: 16px;
  accent-color: var(--el-color-primary);
  cursor: pointer;
}

.col-type {
  flex: 0 0 130px;
  min-width: 0;
}

.col-msg {
  flex: 2;
  min-width: 0;
}

.col-user {
  flex: 0 0 100px;
}

.col-severity {
  flex: 0 0 80px;
}

.col-source {
  flex: 0 0 80px;
}

.col-env {
  flex: 0 0 90px;
}

.col-count {
  flex: 0 0 60px;
  text-align: center;
}

.col-status {
  flex: 0 0 80px;
}

.col-time {
  flex: 1;
  min-width: 0;
}

.col-actions {
  flex: 0 0 80px;
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: flex-end;
}

/* ── 类型标签 ── */
.type-badge {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
  background: var(--el-fill-color);
  color: var(--el-text-color-primary);
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ── 消息 ── */
.msg-text {
  font-size: 13px;
  color: var(--el-text-color-regular);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

/* ── 用户 ── */
.user-text {
  font-size: 13px;
  color: var(--el-text-color-regular);
}

/* ── 严重级别 ── */
.sev-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
}

.sev-debug { background: rgba(99, 102, 241, 0.1); color: #6366f1; }
.sev-warning { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.sev-error { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.sev-critical { background: #ef4444; color: #fff; }

/* ── 来源 ── */
.src-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
}

.src-frontend { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.src-backend { background: rgba(99, 102, 241, 0.1); color: #6366f1; }

/* ── 环境 ── */
.env-text {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

/* ── 次数 ── */
.count-value {
  font-size: 15px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  font-variant-numeric: tabular-nums;
}

/* ── 状态 ── */
.status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
}

.st-unresolved { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.st-resolved { background: rgba(34, 197, 94, 0.1); color: #22c55e; }
.st-ignored { background: var(--el-fill-color); color: var(--el-text-color-secondary); }

/* ── 时间 ── */
.time-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* ── 操作按钮 ── */
.action-btn {
  width: 30px;
  height: 30px;
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
  width: 15px;
  height: 15px;
}

.action-btn:hover { background: var(--el-fill-color); }
.action-view:hover { color: #3b82f6; }
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

/* ── 底部栏 ── */
.bottom-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-shrink: 0;
  gap: 16px;
}

.batch-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  border-radius: 10px;
  background: rgba(239, 68, 68, 0.06);
  border: 1px solid rgba(239, 68, 68, 0.15);
}

.batch-count {
  font-size: 13px;
  font-weight: 600;
  color: #ef4444;
}

.batch-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 8px;
  border: none;
  background: #ef4444;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.batch-btn:hover {
  background: #dc2626;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

/* ── 滑入动画 ── */
.slide-up-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .errors-page {
    padding: 16px;
    gap: 14px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .stats-row {
    grid-template-columns: 1fr;
  }

  .filter-row {
    flex-direction: column;
  }

  .filter-item,
  .search-box {
    flex: 1 1 100%;
    min-width: 0;
    width: 100%;
  }

  .col-user,
  .col-env,
  .col-time {
    display: none;
  }

  .col-actions {
    flex: 0 0 60px;
  }

  .table-header,
  .table-row {
    padding: 10px 12px;
  }

  .bottom-bar {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
