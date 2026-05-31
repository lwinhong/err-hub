<template>
  <div class="error-detail">
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/projects' }">项目列表</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: `/projects/${error.project_id}/errors` }">异常列表</el-breadcrumb-item>
      <el-breadcrumb-item>异常详情</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card shadow="hover" class="info-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">异常信息</span>
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="异常类型" :span="2">
          <span class="exception-type">{{ error.exception_type }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="消息" :span="2">{{ error.message }}</el-descriptions-item>
        <el-descriptions-item label="级别">
          <el-tag :type="severityType(error.severity)" :effect="error.severity === 'critical' ? 'dark' : 'light'" size="small">
            {{ error.severity }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="环境">{{ error.environment }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(error.status)" size="small">{{ statusLabel(error.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="出现次数">{{ error.count }}</el-descriptions-item>
        <el-descriptions-item label="首次出现">{{ formatTime(error.first_seen_at) }}</el-descriptions-item>
        <el-descriptions-item label="最近出现">{{ formatTime(error.last_seen_at) }}</el-descriptions-item>
      </el-descriptions>

      <div class="action-bar">
        <el-button-group>
          <el-button :type="error.status === 'unresolved' ? 'danger' : ''" @click="changeStatus('unresolved')">
            标记为未解决
          </el-button>
          <el-button :type="error.status === 'resolved' ? 'success' : ''" @click="changeStatus('resolved')">
            标记为已解决
          </el-button>
          <el-button :type="error.status === 'ignored' ? 'info' : ''" @click="changeStatus('ignored')">
            标记为忽略
          </el-button>
        </el-button-group>
      </div>
    </el-card>

    <el-card shadow="hover" class="stack-card">
      <template #header>
        <span class="card-title">堆栈信息</span>
      </template>
      <pre class="stack-trace">{{ error.stack_trace || '无堆栈信息' }}</pre>
    </el-card>

    <el-card shadow="hover" class="context-card">
      <template #header>
        <span class="card-title">上下文信息</span>
      </template>
      <pre class="context-data">{{ formatContext(error.context) }}</pre>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getError, updateError } from '../api/errors'

const route = useRoute()
const router = useRouter()
const errorId = route.params.id

const error = ref({})

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

const formatTime = (t) => {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

const formatContext = (ctx) => {
  if (!ctx) return '无上下文信息'
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
    ElMessage.success('状态已更新')
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '更新失败')
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

onMounted(() => {
  fetchError()
})
</script>

<style scoped>
.error-detail {
  padding: 20px;
}

.breadcrumb {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.exception-type {
  font-family: 'Courier New', Courier, monospace;
  font-weight: 600;
  color: #303133;
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
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 6px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  color: #303133;
}
</style>
