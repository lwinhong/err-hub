<template>
  <div class="dashboard">
    <!-- 项目筛选 -->
    <div class="filter-bar">
      <el-select v-model="selectedProjectId" placeholder="全部项目" clearable @change="refreshData" style="width: 220px">
        <el-option label="全部项目" value="" />
        <el-option v-for="p in projectList" :key="p.id" :label="p.name" :value="p.id" />
      </el-select>
    </div>

    <!-- 统计卡片 Row 1 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="4" v-for="card in statCards" :key="card.key">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">{{ card.label }}</div>
              <div class="stat-value">{{ card.value }}</div>
            </div>
            <div class="stat-icon" :style="{ backgroundColor: card.bg, color: card.color }">
              <el-icon :size="32"><component :is="card.icon" /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势图 -->
    <el-card shadow="hover" class="chart-card">
      <template #header>
        <div class="chart-header">
          <span class="card-title">异常趋势</span>
          <el-radio-group v-model="trendDays" size="small" @change="refreshData">
            <el-radio-button :value="7">7天</el-radio-button>
            <el-radio-button :value="14">14天</el-radio-button>
            <el-radio-button :value="30">30天</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <v-chart :option="trendOption" style="height: 320px" autoresize />
    </el-card>

    <!-- 分布图 Row -->
    <el-row :gutter="16" class="chart-row">
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><span class="card-title">严重级别分布</span></template>
          <v-chart :option="severityOption" style="height: 260px" autoresize />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><span class="card-title">来源分布</span></template>
          <v-chart :option="sourceOption" style="height: 260px" autoresize />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><span class="card-title">状态分布</span></template>
          <v-chart :option="statusOption" style="height: 260px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- 排名 Row -->
    <el-row :gutter="16" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="card-title">Top 5 异常类型</span></template>
          <v-chart :option="topErrorsOption" style="height: 280px" autoresize />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="card-title">项目异常排名</span></template>
          <v-chart :option="projectRankOption" style="height: 280px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近异常 -->
    <el-card shadow="hover" class="table-card">
      <template #header><span class="card-title">最近异常</span></template>
      <el-table :data="recentErrors" stripe @row-click="goToError">
        <el-table-column prop="exception_type" label="异常类型" min-width="150" />
        <el-table-column prop="message" label="消息" min-width="200" show-overflow-tooltip />
        <el-table-column prop="project_name" label="项目" width="150" />
        <el-table-column prop="source" label="来源" width="90">
          <template #default="{ row }">
            <el-tag :type="row.source === 'frontend' ? 'warning' : 'primary'" size="small" effect="plain">
              {{ sourceLabel(row.source) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="severityType(row.severity)" size="small">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_seen_at" label="最近出现" width="180">
          <template #default="{ row }">{{ formatTime(row.last_seen_at) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDark } from '@vueuse/core'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import {
  GridComponent, TooltipComponent, LegendComponent, TitleComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getOverview, getDistributions } from '../api/dashboard'
import { getProjects } from '../api/projects'
import { formatTime } from '../utils/format'

use([
  LineChart, BarChart, PieChart,
  GridComponent, TooltipComponent, LegendComponent, TitleComponent,
  CanvasRenderer
])

const router = useRouter()
const isDark = useDark()

const chartTextColor = computed(() => isDark.value ? '#CFD3DC' : '#606266')
const chartAxisLineColor = computed(() => isDark.value ? '#4C4D4F' : '#E4E7ED')
const chartSplitLineColor = computed(() => isDark.value ? '#363637' : '#EBEEF5')

const overview = ref({})
const distributions = ref({})
const recentErrors = ref([])
const projectList = ref([])
const selectedProjectId = ref('')
const trendDays = ref(7)

// ─── stat cards ───
const statCards = computed(() => {
  const o = overview.value
  const totalErrors = o.total_errors || 0
  const resolved = o.resolved_count || 0
  const unresolved = o.unresolved_count || 0
  const resolveRate = totalErrors > 0
    ? ((resolved / totalErrors) * 100).toFixed(1) + '%'
    : '-'

  return [
    { key: 'projects', label: '项目总数', value: o.project_count || 0, icon: 'FolderOpened', bg: 'rgba(64,158,255,0.1)', color: '#409eff' },
    { key: 'total', label: '异常总数', value: totalErrors, icon: 'DataLine', bg: 'rgba(103,194,58,0.1)', color: '#67c23a' },
    { key: 'unresolved', label: '未解决', value: unresolved, icon: 'WarningFilled', bg: 'rgba(245,108,108,0.1)', color: '#f56c6c' },
    { key: 'critical', label: '严重异常', value: o.critical_count || 0, icon: 'CircleCloseFilled', bg: 'rgba(230,0,0,0.08)', color: '#e60000' },
    { key: 'today', label: '今日新增', value: o.today_new_count || 0, icon: 'AlarmClock', bg: 'rgba(230,162,60,0.1)', color: '#e6a23c' },
    { key: 'rate', label: '解决率', value: resolveRate, icon: 'TrendCharts', bg: 'rgba(144,147,153,0.1)', color: '#909399' },
  ]
})

// ─── trend chart ───
const trendOption = computed(() => {
  const trend = overview.value.trend || []
  const dates = trend.map(t => {
    if (!t.date) return ''
    const dateStr = t.date.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(t.date) ? t.date : t.date + 'Z'
    const d = new Date(dateStr)
    return `${d.getMonth() + 1}/${d.getDate()}`
  })
  const counts = trend.map(t => t.count)
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: dates, axisLine: { lineStyle: { color: chartAxisLineColor.value } }, axisLabel: { color: chartTextColor.value } },
    yAxis: { type: 'value', minInterval: 1, axisLine: { lineStyle: { color: chartAxisLineColor.value } }, axisLabel: { color: chartTextColor.value }, splitLine: { lineStyle: { color: chartSplitLineColor.value } } },
    series: [{
      name: '异常数',
      type: 'line',
      smooth: true,
      data: counts,
      areaStyle: { color: 'rgba(64,158,255,0.15)' },
      lineStyle: { color: '#409eff' },
      itemStyle: { color: '#409eff' }
    }]
  }
})

// ─── severity pie ───
const severityOption = computed(() => {
  const data = distributions.value.by_severity || {}
  const colorMap = { debug: '#909399', info: '#909399', warning: '#e6a23c', error: '#f56c6c', critical: '#e60000' }
  const pieData = Object.entries(data).map(([name, value]) => ({
    name,
    value,
    itemStyle: { color: colorMap[name] || '#409eff' }
  }))
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { color: chartTextColor.value } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      data: pieData,
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14 } }
    }]
  }
})

// ─── source pie ───
const sourceOption = computed(() => {
  const data = distributions.value.by_source || {}
  const colorMap = { frontend: '#e6a23c', backend: '#409eff' }
  const labelMap = { frontend: '前端', backend: '后端' }
  const pieData = Object.entries(data).map(([name, value]) => ({
    name: labelMap[name] || name,
    value,
    itemStyle: { color: colorMap[name] || '#909399' }
  }))
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { color: chartTextColor.value } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      data: pieData,
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14 } }
    }]
  }
})

// ─── status pie ───
const statusOption = computed(() => {
  const data = distributions.value.by_status || {}
  const colorMap = { unresolved: '#f56c6c', resolved: '#67c23a', ignored: '#909399' }
  const labelMap = { unresolved: '未解决', resolved: '已解决', ignored: '已忽略' }
  const pieData = Object.entries(data).map(([name, value]) => ({
    name: labelMap[name] || name,
    value,
    itemStyle: { color: colorMap[name] || '#409eff' }
  }))
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { color: chartTextColor.value } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      data: pieData,
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14 } }
    }]
  }
})

// ─── top errors bar ───
const topErrorsOption = computed(() => {
  const items = distributions.value.top_errors || []
  const names = items.map(i => i.exception_type).reverse()
  const counts = items.map(i => i.count).reverse()
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '8%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', minInterval: 1, axisLine: { lineStyle: { color: chartAxisLineColor.value } }, axisLabel: { color: chartTextColor.value }, splitLine: { lineStyle: { color: chartSplitLineColor.value } } },
    yAxis: { type: 'category', data: names, axisLine: { lineStyle: { color: chartAxisLineColor.value } }, axisLabel: { width: 100, overflow: 'truncate', color: chartTextColor.value } },
    series: [{
      type: 'bar',
      data: counts,
      itemStyle: { color: '#f56c6c', borderRadius: [0, 4, 4, 0] },
      barMaxWidth: 24,
    }]
  }
})

// ─── project ranking bar ───
const projectRankOption = computed(() => {
  const items = distributions.value.project_ranking || []
  const names = items.map(i => i.name).reverse()
  const counts = items.map(i => i.total_count).reverse()
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '8%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', minInterval: 1, axisLine: { lineStyle: { color: chartAxisLineColor.value } }, axisLabel: { color: chartTextColor.value }, splitLine: { lineStyle: { color: chartSplitLineColor.value } } },
    yAxis: { type: 'category', data: names, axisLine: { lineStyle: { color: chartAxisLineColor.value } }, axisLabel: { width: 100, overflow: 'truncate', color: chartTextColor.value } },
    series: [{
      type: 'bar',
      data: counts,
      itemStyle: { color: '#409eff', borderRadius: [0, 4, 4, 0] },
      barMaxWidth: 24,
    }]
  }
})

// ─── helpers ───
const severityType = (severity) => {
  const map = { debug: 'info', warning: 'warning', error: 'danger', critical: 'danger' }
  return map[severity] || 'info'
}
const sourceLabel = (source) => {
  const map = { frontend: '前端', backend: '后端' }
  return map[source] || source
}
const goToError = (row) => {
  router.push(`/errors/${row.id}`)
}

// ─── data fetching ───
const refreshData = async () => {
  const params = { days: trendDays.value }
  if (selectedProjectId.value) params.project_id = selectedProjectId.value

  const [overviewRes, distRes] = await Promise.all([
    getOverview(params),
    getDistributions(selectedProjectId.value ? { project_id: selectedProjectId.value } : {})
  ])
  overview.value = overviewRes.data
  recentErrors.value = overviewRes.data.recent_errors || []
  distributions.value = distRes.data
}

const fetchProjects = async () => {
  try {
    const res = await getProjects({ page: 1, per_page: 100 })
    projectList.value = res.data.items || []
  } catch {}
}

onMounted(() => {
  fetchProjects()
  refreshData()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.filter-bar {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
}

.stat-row {
  margin-bottom: 16px;
}

.stat-card {
  height: 100%;
}

.chart-card {
  margin-bottom: 16px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-row {
  margin-bottom: 16px;
}

.table-card {
  margin-bottom: 20px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
}

:deep(.el-table__row) {
  cursor: pointer;
}
</style>
