<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stat-row">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">项目总数</div>
              <div class="stat-value">{{ overview.project_count || 0 }}</div>
            </div>
            <div class="stat-icon blue">
              <el-icon :size="40"><FolderOpened /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">未解决异常</div>
              <div class="stat-value">{{ overview.unresolved_count || 0 }}</div>
            </div>
            <div class="stat-icon red">
              <el-icon :size="40"><WarningFilled /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">今日新增异常</div>
              <div class="stat-value">{{ overview.today_new_count || 0 }}</div>
            </div>
            <div class="stat-icon orange">
              <el-icon :size="40"><AlarmClock /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" class="chart-card">
      <template #header>
        <span class="card-title">异常趋势（最近7天）</span>
      </template>
      <v-chart :option="trendOption" style="height: 350px" autoresize />
    </el-card>

    <el-card shadow="hover" class="table-card">
      <template #header>
        <span class="card-title">最近异常</span>
      </template>
      <el-table :data="recentErrors" stripe @row-click="goToError">
        <el-table-column prop="exception_type" label="异常类型" min-width="150" />
        <el-table-column prop="message" label="消息" min-width="200" show-overflow-tooltip />
        <el-table-column prop="project_name" label="项目" width="150" />
        <el-table-column prop="severity" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="severityType(row.severity)" size="small">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_seen_at" label="最近出现" width="180">
          <template #default="{ row }">
            {{ formatTime(row.last_seen_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getOverview } from '../api/dashboard'

use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const router = useRouter()

const overview = ref({})
const recentErrors = ref([])

const trendOption = computed(() => {
  const trend = overview.value.trend || []
  const dates = trend.map(t => {
    if (!t.date) return ''
    const d = new Date(t.date)
    return `${d.getMonth() + 1}/${d.getDate()}`
  })
  const counts = trend.map(t => t.count)
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [
      {
        name: '异常数',
        type: 'line',
        smooth: true,
        data: counts,
        areaStyle: { color: 'rgba(64,158,255,0.15)' },
        lineStyle: { color: '#409eff' },
        itemStyle: { color: '#409eff' }
      }
    ]
  }
})

const severityType = (severity) => {
  const map = { debug: 'info', warning: 'warning', error: 'danger', critical: 'danger' }
  return map[severity] || 'info'
}

const formatTime = (t) => {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

const goToError = (row) => {
  router.push(`/errors/${row.id}`)
}

const fetchData = async () => {
  try {
    const res = await getOverview()
    overview.value = res.data
    recentErrors.value = res.data.recent_errors || []
  } catch {}
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 100%;
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
}

.stat-icon {
  width: 70px;
  height: 70px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.blue {
  background-color: rgba(64, 158, 255, 0.1);
  color: #409eff;
}

.stat-icon.red {
  background-color: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

.stat-icon.orange {
  background-color: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
}

.chart-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

:deep(.el-table__row) {
  cursor: pointer;
}
</style>
