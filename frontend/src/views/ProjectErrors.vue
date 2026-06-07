<template>
  <div class="project-errors">
    <div class="page-header">
      <h2>{{ projectName }} - 异常列表</h2>
    </div>

    <el-card shadow="hover" class="filter-card">
      <div class="filter-grid">
        <el-select v-model="filters.severity" placeholder="级别" clearable @change="fetchErrors" class="filter-item">
          <el-option label="Debug" value="debug" />
          <el-option label="Warning" value="warning" />
          <el-option label="Error" value="error" />
          <el-option label="Critical" value="critical" />
        </el-select>
        <el-select v-model="filters.environment" placeholder="环境" clearable @change="fetchErrors" class="filter-item">
          <el-option label="Production" value="production" />
          <el-option label="Staging" value="staging" />
          <el-option label="Development" value="development" />
        </el-select>
        <el-select v-model="filters.source" placeholder="来源" clearable @change="fetchErrors" class="filter-item">
          <el-option label="前端" value="frontend" />
          <el-option label="后端" value="backend" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" clearable @change="fetchErrors" class="filter-item">
          <el-option label="未解决" value="unresolved" />
          <el-option label="已解决" value="resolved" />
          <el-option label="已忽略" value="ignored" />
        </el-select>
        <el-input v-model="filters.search" placeholder="搜索异常类型或消息" clearable @clear="fetchErrors" @keyup.enter="fetchErrors" class="filter-item filter-search">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filters.sort" placeholder="排序" @change="fetchErrors" class="filter-item">
          <el-option label="最近出现" value="last_seen_at" />
          <el-option label="出现次数" value="count" />
          <el-option label="首次出现" value="first_seen_at" />
        </el-select>
        <div class="filter-actions">
          <el-button type="primary" @click="fetchErrors">筛选</el-button>
          <el-button
            v-if="authStore.isAdmin && selectedIds.length > 0"
            type="danger"
            @click="handleBatchDelete"
          >
            批量删除 ({{ selectedIds.length }})
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card shadow="hover">
      <div class="table-scroll">
        <el-table :data="errors" stripe v-loading="loading" @row-click="goToError" @selection-change="handleSelectionChange">
        <el-table-column v-if="authStore.isAdmin" type="selection" width="45" @click.stop />
        <el-table-column prop="exception_type" label="异常类型" min-width="160" show-overflow-tooltip />
        <el-table-column prop="message" label="消息" min-width="200" show-overflow-tooltip />
        <el-table-column prop="severity" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="severityType(row.severity)" size="small" :effect="row.severity === 'critical' ? 'dark' : 'light'">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="90">
          <template #default="{ row }">
            <el-tag :type="row.source === 'frontend' ? 'warning' : 'primary'" size="small" effect="plain">
              {{ sourceLabel(row.source) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="environment" label="环境" width="110" />
        <el-table-column prop="count" label="出现次数" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_seen_at" label="最近出现" width="180">
          <template #default="{ row }">{{ formatTime(row.last_seen_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" :width="authStore.isAdmin ? 120 : 60" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click.stop="goToError(row)">详情</el-button>
            <el-button v-if="authStore.isAdmin" link type="danger" @click.stop="handleDelete(row)">删除</el-button>
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
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProjectErrors, deleteError, batchDeleteErrors } from '../api/errors'
import { getProject } from '../api/projects'
import { formatTime } from '../utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const projectId = route.params.id

const projectName = ref('')
const loading = ref(false)
const errors = ref([])
const selectedIds = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filters = reactive({
  severity: '',
  environment: '',
  source: '',
  status: '',
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
  const map = { unresolved: '未解决', resolved: '已解决', ignored: '已忽略' }
  return map[status] || status
}

const sourceLabel = (source) => {
  const map = { frontend: '前端', backend: '后端' }
  return map[source] || source
}


const goToError = (row) => {
  router.push(`/errors/${row.id}`)
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除异常「${row.exception_type}: ${row.message}」吗？`,
      '删除确认',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
    await deleteError(row.id)
    ElMessage.success('删除成功')
    fetchErrors()
  } catch {}
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 条异常吗？`,
      '批量删除确认',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
    const res = await batchDeleteErrors(selectedIds.value)
    ElMessage.success(`成功删除 ${res.data.deleted} 条异常`)
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
    if (filters.severity) params.severity = filters.severity
    if (filters.environment) params.environment = filters.environment
    if (filters.source) params.source = filters.source
    if (filters.status) params.status = filters.status
    if (filters.search) params.search = filters.search
    if (filters.sort) params.sort = filters.sort
    const res = await getProjectErrors(projectId, params)
    errors.value = res.data.items || res.data
    total.value = res.data.total || errors.value.length
  } catch {} finally {
    loading.value = false
  }
}

const fetchProject = async () => {
  try {
    const res = await getProject(projectId)
    projectName.value = res.data.name
  } catch {}
}

onMounted(() => {
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
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
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
