<template>
  <div class="project-errors">
    <div class="page-header">
      <h2>
        <router-link to="/projects" class="project-back-link">{{ projectName }}</router-link>
        <span class="title-suffix">{{ t('projectErrors.titleSuffix') }}</span>
      </h2>
      <el-select
        :model-value="projectId"
        :placeholder="t('projectErrors.switchProject')"
        size="small"
        style="width: 200px"
        @change="switchProject"
      >
        <el-option v-for="p in projectList" :key="p.id" :label="p.name" :value="p.id" />
      </el-select>
    </div>

    <el-card shadow="hover" class="filter-card">
      <div class="filter-grid">
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
        <el-input v-model="filters.search" :placeholder="t('projectErrors.searchPlaceholder')" clearable @clear="fetchErrors" @keyup.enter="fetchErrors" class="filter-item filter-search">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filters.sort" :placeholder="t('projectErrors.sort')" @change="fetchErrors" class="filter-item">
          <el-option :label="t('projectErrors.lastSeen')" value="last_seen_at" />
          <el-option :label="t('projectErrors.count')" value="count" />
          <el-option :label="t('projectErrors.firstSeen')" value="first_seen_at" />
        </el-select>
        <div class="filter-actions">
          <el-button type="primary" @click="fetchErrors">{{ t('projectErrors.filter') }}</el-button>
          <el-button
            v-if="authStore.isAdmin && selectedIds.length > 0"
            type="danger"
            @click="handleBatchDelete"
          >
            {{ t('projectErrors.batchDelete', { count: selectedIds.length }) }}
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card shadow="hover">
      <div class="table-scroll">
        <el-table :data="errors" stripe v-loading="loading" @row-click="goToError" @selection-change="handleSelectionChange">
        <el-table-column v-if="authStore.isAdmin" type="selection" width="45" @click.stop />
        <el-table-column prop="exception_type" :label="t('projectErrors.exceptionType')" min-width="160" show-overflow-tooltip />
        <el-table-column prop="message" :label="t('projectErrors.message')" min-width="200" show-overflow-tooltip />
        <el-table-column prop="severity" :label="t('projectErrors.severity')" width="100">
          <template #default="{ row }">
            <el-tag :type="severityType(row.severity)" size="small" :effect="row.severity === 'critical' ? 'dark' : 'light'">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" :label="t('projectErrors.source')" width="90">
          <template #default="{ row }">
            <el-tag :type="row.source === 'frontend' ? 'warning' : 'primary'" size="small" effect="plain">
              {{ sourceLabel(row.source) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="environment" :label="t('projectErrors.environment')" width="110" />
        <el-table-column prop="count" :label="t('projectErrors.count')" width="100" />
        <el-table-column prop="status" :label="t('projectErrors.status')" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_seen_at" :label="t('projectErrors.lastSeen')" width="180">
          <template #default="{ row }">{{ formatTime(row.last_seen_at) }}</template>
        </el-table-column>
        <el-table-column :label="t('projectErrors.actions')" :width="authStore.isAdmin ? 120 : 60" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click.stop="goToError(row)">{{ t('projectErrors.detail') }}</el-button>
            <el-button v-if="authStore.isAdmin" link type="danger" @click.stop="handleDelete(row)">{{ t('projectErrors.delete') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      </div>
      <div class="pagination-wrapper">
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
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { getProjectErrors, deleteError, batchDeleteErrors } from '../api/errors'
import { getProject, getProjects } from '../api/projects'
import { formatTime } from '../utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()
const projectId = computed(() => route.params.id)

const projectName = ref('')
const projectList = ref([])
const loading = ref(false)
const errors = ref([])
const selectedIds = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filters = reactive({
  severity: [],
  environment: [],
  source: [],
  status: [],
  search: '',
  sort: 'last_seen_at'
})

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

onMounted(() => {
  fetchProjects()
  fetchProject()
  fetchErrors()
})
</script>

<style scoped>
.project-errors {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: var(--el-text-color-primary);
}

.project-back-link {
  color: var(--el-color-primary);
  text-decoration: none;
  transition: opacity 0.15s;
}

.project-back-link:hover {
  opacity: 0.75;
  text-decoration: underline;
}

.title-suffix {
  margin-left: 8px;
  color: var(--el-text-color-primary);
}

.filter-card {
  margin-bottom: 16px;
}

.filter-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.filter-item {
  flex: 1 1 140px;
  min-width: 120px;
}

.filter-search {
  flex: 2 1 200px;
  min-width: 180px;
}

.filter-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.table-scroll {
  overflow-x: auto;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

:deep(.el-table__row) {
  cursor: pointer;
}

@media (max-width: 768px) {
  .project-errors {
    padding: 12px;
  }

  .filter-grid {
    flex-direction: column;
  }

  .filter-item,
  .filter-search {
    flex: 1 1 100%;
    min-width: 0;
    width: 100%;
  }

  .filter-actions {
    width: 100%;
  }

  .filter-actions .el-button {
    flex: 1;
  }

  .pagination-wrapper {
    justify-content: center;
  }

  .pagination-wrapper :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
