<template>
  <div class="dashboard-page">
    <!-- 标题区 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon">
          <el-icon :size="28"><DataAnalysis /></el-icon>
        </div>
        <div>
          <h2 class="header-title">{{ t('app.dashboard') }}</h2>
          <p class="header-subtitle">{{ t('dashboard.subtitle') }}</p>
        </div>
      </div>
      <el-select
        v-model="selectedProjectId"
        :placeholder="t('dashboard.allProjects')"
        clearable
        @change="refreshData"
        size="large"
        style="width: 220px"
      >
        <el-option :label="t('dashboard.allProjects')" value="" />
        <el-option v-for="p in projectList" :key="p.id" :label="p.name" :value="p.id" />
      </el-select>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div
        v-for="card in statCards"
        :key="card.key"
        class="stat-card"
        :class="'stat-' + card.key"
        :style="{ cursor: card.route ? 'pointer' : 'default' }"
        @click="card.route && router.push(card.route)"
      >
        <div class="stat-icon" :style="{ background: card.bg, color: card.color }">
          <el-icon :size="24"><component :is="card.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ card.value }}</span>
          <span class="stat-label">{{ card.label }}</span>
        </div>
        <div v-if="card.extra" class="stat-extra">
          <span :style="{ color: card.extraColor }">{{ card.extra }}</span>
          <span class="stat-extra-label">{{ card.extraLabel }}</span>
        </div>
      </div>
    </div>

    <!-- 趋势图 + 环境分布 -->
    <div class="chart-row">
      <div class="chart-card chart-wide">
        <div class="chart-header">
          <h3 class="chart-title">{{ t('dashboard.errorTrend') }}</h3>
          <el-radio-group v-model="trendDays" size="small" @change="refreshData">
            <el-radio-button :value="7">{{ t('dashboard.days7') }}</el-radio-button>
            <el-radio-button :value="14">{{ t('dashboard.days14') }}</el-radio-button>
            <el-radio-button :value="30">{{ t('dashboard.days30') }}</el-radio-button>
          </el-radio-group>
        </div>
        <v-chart :option="trendOption" style="height: 300px" autoresize />
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">{{ t('dashboard.environmentDistribution') }}</h3>
        </div>
        <v-chart :option="environmentOption" style="height: 300px" autoresize />
      </div>
    </div>

    <!-- 分布图 -->
    <div class="chart-row chart-row-3">
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">{{ t('dashboard.severityDistribution') }}</h3>
        </div>
        <v-chart :option="severityOption" style="height: 260px" autoresize />
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">{{ t('dashboard.sourceDistribution') }}</h3>
        </div>
        <v-chart :option="sourceOption" style="height: 260px" autoresize />
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">{{ t('dashboard.statusDistribution') }}</h3>
        </div>
        <v-chart :option="statusOption" style="height: 260px" autoresize />
      </div>
    </div>

    <!-- 排名 -->
    <div class="chart-row">
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">{{ t('dashboard.topErrors') }}</h3>
        </div>
        <v-chart :option="topErrorsOption" style="height: 280px" autoresize />
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">{{ t('dashboard.projectRanking') }}</h3>
        </div>
        <v-chart :option="projectRankOption" style="height: 280px" autoresize />
      </div>
    </div>

    <!-- 最近异常 -->
    <div class="recent-section">
      <div class="recent-header">
        <h3 class="chart-title">{{ t('dashboard.recentErrors') }}</h3>
        <div class="recent-filters">
          <el-switch v-model="hideResolved" :active-text="t('dashboard.hideResolved')" size="small" @change="refreshData" />
          <el-select v-model="recentProjectId" :placeholder="t('dashboard.allProjects')" clearable multiple collapse-tags collapse-tags-tooltip size="small" style="width: 260px" @change="refreshData">
            <el-option v-for="p in projectList" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </div>
      </div>
      <div class="recent-table-wrap">
        <div class="table-header">
          <span class="col-type">{{ t('dashboard.exceptionType') }}</span>
          <span class="col-msg">{{ t('dashboard.message') }}</span>
          <span class="col-count">{{ t('dashboard.count') }}</span>
          <span class="col-project">{{ t('dashboard.project') }}</span>
          <span class="col-env">{{ t('dashboard.environment') }}</span>
          <span class="col-source">{{ t('dashboard.source') }}</span>
          <span class="col-severity">{{ t('dashboard.severity') }}</span>
          <span class="col-status">{{ t('dashboard.status') }}</span>
          <span class="col-time">{{ t('dashboard.lastSeen') }}</span>
        </div>
        <div v-for="row in recentErrors" :key="row.id" class="table-row" @click="goToError(row)">
          <div class="col-type">
            <span class="type-badge">{{ row.exception_type }}</span>
          </div>
          <div class="col-msg">
            <span class="msg-text" :title="row.message">{{ row.message }}</span>
          </div>
          <div class="col-count">
            <span class="count-value">{{ row.count }}</span>
          </div>
          <div class="col-project">
            <span class="project-tag" :class="'pt-' + projectTagType(row.project_name)">{{ row.project_name }}</span>
          </div>
          <div class="col-env">
            <span v-if="row.environment" class="env-badge" :class="'env-' + row.environment">{{ row.environment }}</span>
            <span v-else>-</span>
          </div>
          <div class="col-source">
            <span class="src-badge" :class="'src-' + row.source">{{ sourceLabel(row.source) }}</span>
          </div>
          <div class="col-severity">
            <span class="sev-badge" :class="'sev-' + row.severity">{{ row.severity }}</span>
          </div>
          <div class="col-status">
            <span class="status-badge" :class="'st-' + row.status">{{ statusLabel(row.status) }}</span>
          </div>
          <div class="col-time">{{ formatTime(row.last_seen_at) }}</div>
        </div>
        <div v-if="recentErrors.length === 0" class="table-empty">
          {{ t('dashboard.noData') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useDark } from '@vueuse/core'
import { DataAnalysis, FolderOpened, DataLine, WarningFilled, CircleCloseFilled, AlarmClock, TrendCharts, Calendar, Aim } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getOverview, getDistributions } from '../api/dashboard'
import { getProjects } from '../api/projects'
import { formatTime } from '../utils/format'

use([LineChart, BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent, CanvasRenderer])

const router = useRouter()
const { t } = useI18n()
const isDark = useDark()

const chartTextColor = computed(() => isDark.value ? '#CFD3DC' : '#606266')
const chartAxisLineColor = computed(() => isDark.value ? '#4C4D4F' : '#E4E7ED')
const chartSplitLineColor = computed(() => isDark.value ? '#363637' : '#EBEEF5')

const overview = ref({})
const distributions = ref({})
const recentErrors = ref([])
const projectList = ref([])
const selectedProjectId = ref('')
const recentProjectId = ref([])
const hideResolved = ref(true)
const trendDays = ref(7)

const statCards = computed(() => {
  const o = overview.value
  const totalErrors = o.total_errors || 0
  const resolved = o.resolved_count || 0
  const unresolved = o.unresolved_count || 0
  const resolveRate = totalErrors > 0 ? ((resolved / totalErrors) * 100).toFixed(1) + '%' : '-'

  const trend = o.trend || []
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const thisMonday = new Date(today)
  thisMonday.setDate(today.getDate() - today.getDay() + 1)
  const lastMonday = new Date(thisMonday)
  lastMonday.setDate(thisMonday.getDate() - 7)

  let thisWeekCount = 0
  let lastWeekCount = 0
  for (const item of trend) {
    if (!item.date) continue
    const dateStr = item.date.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(item.date) ? item.date : item.date + 'Z'
    const d = new Date(dateStr)
    if (d >= thisMonday) thisWeekCount += item.count
    else if (d >= lastMonday) lastWeekCount += item.count
  }

  const weeklyTrendPct = lastWeekCount > 0 ? (((thisWeekCount - lastWeekCount) / lastWeekCount) * 100).toFixed(0) : null
  const weeklyTrendText = weeklyTrendPct !== null ? `${weeklyTrendPct > 0 ? '+' : ''}${weeklyTrendPct}%` : '-'

  const avgDaily = trend.length > 0 ? (trend.reduce((s, t) => s + t.count, 0) / trend.length).toFixed(1) : '0'

  return [
    { key: 'projects', label: t('dashboard.projectCount'), value: o.project_count || 0, icon: FolderOpened, bg: 'rgba(99,102,241,0.1)', color: '#6366f1', route: '/projects' },
    { key: 'total', label: t('dashboard.totalErrors'), value: totalErrors, icon: DataLine, bg: 'rgba(59,130,246,0.1)', color: '#3b82f6' },
    { key: 'unresolved', label: t('dashboard.unresolved'), value: unresolved, icon: WarningFilled, bg: 'rgba(245,158,11,0.1)', color: '#f59e0b' },
    { key: 'critical', label: t('dashboard.criticalErrors'), value: o.critical_count || 0, icon: CircleCloseFilled, bg: 'rgba(239,68,68,0.1)', color: '#ef4444' },
    { key: 'today', label: t('dashboard.todayNew'), value: o.today_new_count || 0, icon: AlarmClock, bg: 'rgba(168,85,247,0.1)', color: '#a855f7' },
    { key: 'weekly', label: t('dashboard.weeklyNew'), value: thisWeekCount, icon: Calendar, bg: 'rgba(34,197,94,0.1)', color: '#22c55e', extra: weeklyTrendText, extraColor: weeklyTrendPct > 0 ? '#ef4444' : weeklyTrendPct < 0 ? '#22c55e' : '#94a3b8', extraLabel: t('dashboard.weeklyTrend') },
    { key: 'avg', label: t('dashboard.avgDaily'), value: avgDaily, icon: Aim, bg: 'rgba(236,72,153,0.1)', color: '#ec4899' },
    { key: 'rate', label: t('dashboard.resolveRate'), value: resolveRate, icon: TrendCharts, bg: 'rgba(20,184,166,0.1)', color: '#14b8a6' },
  ]
})

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
    grid: { left: '3%', right: '4%', bottom: '3%', outerBounds: { contain: 'label' } },
    xAxis: { type: 'category', boundaryGap: false, data: dates, axisLine: { lineStyle: { color: chartAxisLineColor.value } }, axisLabel: { color: chartTextColor.value } },
    yAxis: { type: 'value', minInterval: 1, axisLine: { lineStyle: { color: chartAxisLineColor.value } }, axisLabel: { color: chartTextColor.value }, splitLine: { lineStyle: { color: chartSplitLineColor.value } } },
    series: [{
      name: t('dashboard.errorCount'),
      type: 'line',
      smooth: true,
      data: counts,
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(99,102,241,0.3)' }, { offset: 1, color: 'rgba(99,102,241,0.02)' }] } },
      lineStyle: { color: '#6366f1', width: 3 },
      itemStyle: { color: '#6366f1' },
      symbol: 'circle',
      symbolSize: 6,
    }]
  }
})

const severityOption = computed(() => {
  const data = distributions.value.by_severity || {}
  const colorMap = { debug: '#94a3b8', info: '#94a3b8', warning: '#f59e0b', error: '#ef4444', critical: '#dc2626' }
  const pieData = Object.entries(data).map(([name, value]) => ({ name, value, itemStyle: { color: colorMap[name] || '#6366f1' } }))
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { color: chartTextColor.value } },
    series: [{ type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'], data: pieData, label: { show: false }, emphasis: { label: { show: true, fontSize: 14 } } }]
  }
})

const sourceOption = computed(() => {
  const data = distributions.value.by_source || {}
  const colorMap = { frontend: '#f59e0b', backend: '#6366f1' }
  const labelMap = { frontend: t('dashboard.frontend'), backend: t('dashboard.backend') }
  const pieData = Object.entries(data).map(([name, value]) => ({ name: labelMap[name] || name, value, itemStyle: { color: colorMap[name] || '#94a3b8' } }))
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { color: chartTextColor.value } },
    series: [{ type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'], data: pieData, label: { show: false }, emphasis: { label: { show: true, fontSize: 14 } } }]
  }
})

const statusOption = computed(() => {
  const data = distributions.value.by_status || {}
  const colorMap = { unresolved: '#ef4444', resolved: '#22c55e', ignored: '#94a3b8' }
  const labelMap = { unresolved: t('dashboard.unresolved'), resolved: t('dashboard.resolved'), ignored: t('dashboard.ignored') }
  const pieData = Object.entries(data).map(([name, value]) => ({ name: labelMap[name] || name, value, itemStyle: { color: colorMap[name] || '#6366f1' } }))
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { color: chartTextColor.value } },
    series: [{ type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'], data: pieData, label: { show: false }, emphasis: { label: { show: true, fontSize: 14 } } }]
  }
})

const environmentOption = computed(() => {
  const data = distributions.value.by_environment || {}
  const colorMap = { production: '#ef4444', staging: '#f59e0b', development: '#22c55e' }
  const labelMap = { production: t('dashboard.production'), staging: t('dashboard.staging'), development: t('dashboard.development') }
  const pieData = Object.entries(data).map(([name, value]) => ({ name: labelMap[name] || name, value, itemStyle: { color: colorMap[name] || '#94a3b8' } }))
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { color: chartTextColor.value } },
    series: [{ type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'], data: pieData, label: { show: false }, emphasis: { label: { show: true, fontSize: 14 } } }]
  }
})

const topErrorsOption = computed(() => {
  const items = distributions.value.top_errors || []
  const names = items.map(i => i.exception_type).reverse()
  const counts = items.map(i => i.count).reverse()
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '8%', bottom: '3%', outerBounds: { contain: 'label' } },
    xAxis: { type: 'value', minInterval: 1, axisLine: { lineStyle: { color: chartAxisLineColor.value } }, axisLabel: { color: chartTextColor.value }, splitLine: { lineStyle: { color: chartSplitLineColor.value } } },
    yAxis: { type: 'category', data: names, axisLine: { lineStyle: { color: chartAxisLineColor.value } }, axisLabel: { width: 100, overflow: 'truncate', color: chartTextColor.value } },
    series: [{ type: 'bar', data: counts, itemStyle: { color: '#ef4444', borderRadius: [0, 6, 6, 0] }, barMaxWidth: 24 }]
  }
})

const projectRankOption = computed(() => {
  const items = distributions.value.project_ranking || []
  const names = items.map(i => i.name).reverse()
  const counts = items.map(i => i.total_count).reverse()
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '8%', bottom: '3%', outerBounds: { contain: 'label' } },
    xAxis: { type: 'value', minInterval: 1, axisLine: { lineStyle: { color: chartAxisLineColor.value } }, axisLabel: { color: chartTextColor.value }, splitLine: { lineStyle: { color: chartSplitLineColor.value } } },
    yAxis: { type: 'category', data: names, axisLine: { lineStyle: { color: chartAxisLineColor.value } }, axisLabel: { width: 100, overflow: 'truncate', color: chartTextColor.value } },
    series: [{ type: 'bar', data: counts, itemStyle: { color: '#6366f1', borderRadius: [0, 6, 6, 0] }, barMaxWidth: 24 }]
  }
})

const severityType = (severity) => {
  const map = { debug: 'info', warning: 'warning', error: 'danger', critical: 'danger' }
  return map[severity] || 'info'
}
const sourceLabel = (source) => {
  const map = { frontend: t('dashboard.frontend'), backend: t('dashboard.backend') }
  return map[source] || source
}
const envTagType = (env) => {
  const map = { production: 'danger', staging: 'warning', development: 'info' }
  return map[env] || 'info'
}
const statusType = (status) => {
  const map = { unresolved: 'danger', resolved: 'success', ignored: 'info' }
  return map[status] || 'info'
}
const statusLabel = (status) => {
  const map = { unresolved: t('dashboard.unresolved'), resolved: t('dashboard.resolved'), ignored: t('dashboard.ignored') }
  return map[status] || status
}
const tagTypes = ['primary', 'success', 'warning', 'danger', 'info']
const projectTagType = (name) => {
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = ((hash << 5) - hash + name.charCodeAt(i)) | 0
  return tagTypes[Math.abs(hash) % tagTypes.length]
}
const goToError = (row) => {
  router.push(`/projects/${row.project_id}/errors`)
}

const refreshData = async () => {
  const params = { days: trendDays.value, hide_resolved: hideResolved.value ? 'true' : 'false' }
  if (selectedProjectId.value) params.project_id = selectedProjectId.value
  if (recentProjectId.value.length) params.recent_project_id = recentProjectId.value.join(',')
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
  } catch { }
}

onMounted(() => {
  fetchProjects()
  refreshData()
})
</script>

<style scoped>
.dashboard-page {
  padding: 24px;
  display: flex;
  flex-direction: column;
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
  background: linear-gradient(135deg, #6366f1, #818cf8);
  color: #fff;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35);
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

/* ── 统计卡片 ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 14px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  transition: all 0.2s;
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

.stat-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 22px;
  font-weight: 800;
  line-height: 1;
  color: var(--el-text-color-primary);
  font-variant-numeric: tabular-nums;
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-extra {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  font-size: 13px;
  font-weight: 700;
}

.stat-extra-label {
  font-size: 11px;
  font-weight: 400;
  color: var(--el-text-color-secondary);
}

/* ── 图表卡片 ── */
.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.chart-row-3 {
  grid-template-columns: repeat(3, 1fr);
}

.chart-card {
  border-radius: 14px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  overflow: hidden;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.chart-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

/* ── 最近异常 ── */
.recent-section {
  border-radius: 14px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  overflow: hidden;
}

.recent-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  flex-wrap: wrap;
  gap: 12px;
}

.recent-filters {
  display: flex;
  align-items: center;
  gap: 12px;
}

.recent-table-wrap {
  overflow-x: auto;
}

.table-header {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  background: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color-lighter);
  font-size: 12px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table-row {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  cursor: pointer;
  transition: background 0.15s;
}

.table-row:last-child { border-bottom: none; }
.table-row:hover { background: var(--el-fill-color-lighter); }

.col-type { flex: 0 0 140px; min-width: 0; }
.col-msg { flex: 2; min-width: 0; }
.col-count { flex: 0 0 60px; text-align: center; }
.col-project { flex: 0 0 120px; }
.col-env { flex: 0 0 100px; }
.col-source { flex: 0 0 80px; }
.col-severity { flex: 0 0 80px; }
.col-status { flex: 0 0 80px; }
.col-time { flex: 1; min-width: 0; }

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

.msg-text {
  font-size: 13px;
  color: var(--el-text-color-regular);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}

.count-value {
  font-size: 15px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  font-variant-numeric: tabular-nums;
}

.project-tag {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 6px;
  display: inline-block;
}

.pt-primary { background: rgba(99,102,241,0.1); color: #6366f1; }
.pt-success { background: rgba(34,197,94,0.1); color: #22c55e; }
.pt-warning { background: rgba(245,158,11,0.1); color: #f59e0b; }
.pt-danger { background: rgba(239,68,68,0.1); color: #ef4444; }
.pt-info { background: var(--el-fill-color); color: var(--el-text-color-secondary); }

.env-badge, .src-badge, .sev-badge, .status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
}

.env-production { background: rgba(239,68,68,0.1); color: #ef4444; }
.env-staging { background: rgba(245,158,11,0.1); color: #f59e0b; }
.env-development { background: rgba(34,197,94,0.1); color: #22c55e; }

.src-frontend { background: rgba(245,158,11,0.1); color: #f59e0b; }
.src-backend { background: rgba(99,102,241,0.1); color: #6366f1; }

.sev-debug { background: rgba(148,163,184,0.1); color: #94a3b8; }
.sev-warning { background: rgba(245,158,11,0.1); color: #f59e0b; }
.sev-error { background: rgba(239,68,68,0.1); color: #ef4444; }
.sev-critical { background: #ef4444; color: #fff; }

.st-unresolved { background: rgba(239,68,68,0.1); color: #ef4444; }
.st-resolved { background: rgba(34,197,94,0.1); color: #22c55e; }
.st-ignored { background: var(--el-fill-color); color: var(--el-text-color-secondary); }

.table-empty {
  padding: 40px 20px;
  text-align: center;
  color: var(--el-text-color-placeholder);
  font-size: 14px;
}

/* ── 响应式 ── */
@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(4, 1fr); }
}

@media (max-width: 900px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .chart-row { grid-template-columns: 1fr; }
  .chart-row-3 { grid-template-columns: 1fr; }
  .recent-header { flex-direction: column; align-items: flex-start; }
}

@media (max-width: 768px) {
  .dashboard-page { padding: 16px; gap: 16px; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .stats-grid { grid-template-columns: 1fr 1fr; }
  .col-env, .col-project, .col-time { display: none; }
  .table-header, .table-row { padding: 10px 14px; }
}
</style>
