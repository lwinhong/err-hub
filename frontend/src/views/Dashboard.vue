<template>
  <div class="p-5 max-sm:p-3">
    <!-- 项目筛选 -->
    <div class="mb-4 flex justify-between max-sm:justify-stretch">
      <h2 class="m-0 text-xl max-sm:hidden">{{ t('app.dashboard') }}</h2>
      <div class="w-[220px] max-sm:!w-full">
        <el-select v-model="selectedProjectId" :placeholder="t('dashboard.allProjects')" clearable
          @change="refreshData">
          <el-option :label="t('dashboard.allProjects')" value="" />
          <el-option v-for="p in projectList" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </div>
    </div>

    <!-- 统计卡片 Row 1 -->
    <el-row :gutter="16" class="mb-4 [&>.el-col]:mb-3">
      <el-col :xs="12" :sm="8" :md="6" :lg="4" v-for="card in statCards" :key="card.key">
        <el-card shadow="hover" class="h-full"
          :class="{ 'cursor-pointer transition-transform transition-shadow duration-150 hover:-translate-y-0.5 hover:shadow-[0_4px_12px_rgba(0,0,0,0.1)]': card.route }"
          @click="card.route && router.push(card.route)">
          <div class="flex justify-between items-center">
            <div class="flex-1 min-w-0">
              <div class="text-[13px] mb-1" style="color: var(--el-text-color-secondary)">{{ card.label }}</div>
              <div class="text-2xl max-sm:text-xl font-bold" style="color: var(--el-text-color-primary)">{{ card.value
              }}</div>
              <div v-if="card.extra" class="text-[11px] mt-0.5 flex items-center gap-1">
                <span :style="{ color: card.extraColor }">{{ card.extra }}</span>
                <span style="color: var(--el-text-color-placeholder)">{{ card.extraLabel }}</span>
              </div>
            </div>
            <div class="w-12 h-12 max-sm:w-10 max-sm:h-10 rounded-[10px] flex items-center justify-center shrink-0"
              :style="{ backgroundColor: card.bg, color: card.color }">
              <el-icon :size="28">
                <component :is="card.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势图 + 环境分布 -->
    <el-row :gutter="16" class="mb-4 [&>.el-col]:mb-3">
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover" class="h-full">
          <template #header>
            <div class="flex justify-between items-center flex-wrap gap-2 max-sm:flex-col max-sm:items-start">
              <span class="text-[15px] font-semibold">{{ t('dashboard.errorTrend') }}</span>
              <el-radio-group v-model="trendDays" size="small" @change="refreshData">
                <el-radio-button :value="7">{{ t('dashboard.days7') }}</el-radio-button>
                <el-radio-button :value="14">{{ t('dashboard.days14') }}</el-radio-button>
                <el-radio-button :value="30">{{ t('dashboard.days30') }}</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <v-chart :option="trendOption" style="height: 300px" autoresize />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover" class="h-full">
          <template #header><span class="text-[15px] font-semibold">{{ t('dashboard.environmentDistribution')
              }}</span></template>
          <v-chart :option="environmentOption" style="height: 300px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- 分布图 Row -->
    <el-row :gutter="16" class="mb-4 [&>.el-col]:mb-3">
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover">
          <template #header><span class="text-[15px] font-semibold">{{ t('dashboard.severityDistribution')
              }}</span></template>
          <v-chart :option="severityOption" style="height: 260px" autoresize />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover">
          <template #header><span class="text-[15px] font-semibold">{{ t('dashboard.sourceDistribution')
              }}</span></template>
          <v-chart :option="sourceOption" style="height: 260px" autoresize />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover">
          <template #header><span class="text-[15px] font-semibold">{{ t('dashboard.statusDistribution')
              }}</span></template>
          <v-chart :option="statusOption" style="height: 260px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- 排名 Row -->
    <el-row :gutter="16" class="mb-4 [&>.el-col]:mb-3">
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover">
          <template #header><span class="text-[15px] font-semibold">{{ t('dashboard.topErrors') }}</span></template>
          <v-chart :option="topErrorsOption" style="height: 280px" autoresize />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover">
          <template #header><span class="text-[15px] font-semibold">{{ t('dashboard.projectRanking')
              }}</span></template>
          <v-chart :option="projectRankOption" style="height: 280px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近异常 -->
    <el-card shadow="hover" class="mb-5">
      <template #header>
        <div class="flex justify-between items-center flex-wrap gap-2 max-sm:flex-col max-sm:items-start">
          <span class="text-[15px] font-semibold">{{ t('dashboard.recentErrors') }}</span>
          <div class="flex items-center gap-3">
            <el-switch v-model="hideResolved" :active-text="t('dashboard.hideResolved')" size="small"
              @change="refreshData" />
            <el-select v-model="recentProjectId" :placeholder="t('dashboard.allProjects')" clearable multiple
              collapse-tags collapse-tags-tooltip size="small" style="width: 260px" @change="refreshData">
              <el-option v-for="p in projectList" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </div>
        </div>
      </template>
      <el-table :data="recentErrors" stripe class="dashboard-table" @row-click="goToError">
        <el-table-column prop="exception_type" :label="t('dashboard.exceptionType')" min-width="150" />
        <el-table-column prop="message" :label="t('dashboard.message')" min-width="200" show-overflow-tooltip />
        <el-table-column prop="count" :label="t('dashboard.count')" width="100" />
        <el-table-column prop="project_name" :label="t('dashboard.project')" width="150">
          <template #default="{ row }">
            <el-tag size="small" effect="plain" :type="projectTagType(row.project_name)">{{ row.project_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="environment" :label="t('dashboard.environment')" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.environment" :type="envTagType(row.environment)" size="small" effect="plain">{{
              row.environment }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="source" :label="t('dashboard.source')" width="90">
          <template #default="{ row }">
            <el-tag :type="row.source === 'frontend' ? 'warning' : 'primary'" size="small" effect="plain">
              {{ sourceLabel(row.source) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" :label="t('dashboard.severity')" width="100">
          <template #default="{ row }">
            <el-tag :type="severityType(row.severity)" size="small">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="t('dashboard.status')" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="plain">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_seen_at" :label="t('dashboard.lastSeen')" width="180">
          <template #default="{ row }">{{ formatTime(row.last_seen_at) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useDark } from '@vueuse/core'
import {
  FolderOpened, DataLine, WarningFilled,
  CircleCloseFilled, AlarmClock, TrendCharts,
  Calendar, Aim
} from '@element-plus/icons-vue'
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

// ─── stat cards ───
const statCards = computed(() => {
  const o = overview.value
  const totalErrors = o.total_errors || 0
  const resolved = o.resolved_count || 0
  const unresolved = o.unresolved_count || 0
  const resolveRate = totalErrors > 0
    ? ((resolved / totalErrors) * 100).toFixed(1) + '%'
    : '-'

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

  const weeklyTrendPct = lastWeekCount > 0
    ? (((thisWeekCount - lastWeekCount) / lastWeekCount) * 100).toFixed(0)
    : null
  const weeklyTrendText = weeklyTrendPct !== null
    ? `${weeklyTrendPct > 0 ? '+' : ''}${weeklyTrendPct}%`
    : '-'

  const avgDaily = trend.length > 0
    ? (trend.reduce((s, t) => s + t.count, 0) / trend.length).toFixed(1)
    : '0'

  return [
    { key: 'projects', label: t('dashboard.projectCount'), value: o.project_count || 0, icon: FolderOpened, bg: 'rgba(64,158,255,0.1)', color: '#409eff', route: '/projects' },
    { key: 'total', label: t('dashboard.totalErrors'), value: totalErrors, icon: DataLine, bg: 'rgba(103,194,58,0.1)', color: '#67c23a' },
    { key: 'unresolved', label: t('dashboard.unresolved'), value: unresolved, icon: WarningFilled, bg: 'rgba(245,108,108,0.1)', color: '#f56c6c' },
    { key: 'critical', label: t('dashboard.criticalErrors'), value: o.critical_count || 0, icon: CircleCloseFilled, bg: 'rgba(230,0,0,0.08)', color: '#e60000' },
    { key: 'today', label: t('dashboard.todayNew'), value: o.today_new_count || 0, icon: AlarmClock, bg: 'rgba(230,162,60,0.1)', color: '#e6a23c' },
    { key: 'weekly', label: t('dashboard.weeklyNew'), value: thisWeekCount, icon: Calendar, bg: 'rgba(103,194,58,0.1)', color: '#67c23a', extra: weeklyTrendText, extraColor: weeklyTrendPct > 0 ? '#f56c6c' : weeklyTrendPct < 0 ? '#67c23a' : '#909399', extraLabel: t('dashboard.weeklyTrend') },
    { key: 'avg', label: t('dashboard.avgDaily'), value: avgDaily, icon: Aim, bg: 'rgba(144,147,153,0.1)', color: '#909399' },
    { key: 'rate', label: t('dashboard.resolveRate'), value: resolveRate, icon: TrendCharts, bg: 'rgba(144,147,153,0.1)', color: '#909399' },
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
    grid: { left: '3%', right: '4%', bottom: '3%', outerBounds: { contain: 'label' } },
    xAxis: { type: 'category', boundaryGap: false, data: dates, axisLine: { lineStyle: { color: chartAxisLineColor.value } }, axisLabel: { color: chartTextColor.value } },
    yAxis: { type: 'value', minInterval: 1, axisLine: { lineStyle: { color: chartAxisLineColor.value } }, axisLabel: { color: chartTextColor.value }, splitLine: { lineStyle: { color: chartSplitLineColor.value } } },
    series: [{
      name: t('dashboard.errorCount'),
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
  const labelMap = { frontend: t('dashboard.frontend'), backend: t('dashboard.backend') }
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
  const labelMap = { unresolved: t('dashboard.unresolved'), resolved: t('dashboard.resolved'), ignored: t('dashboard.ignored') }
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

// ─── environment pie ───
const environmentOption = computed(() => {
  const data = distributions.value.by_environment || {}
  const colorMap = { production: '#e60000', staging: '#e6a23c', development: '#67c23a' }
  const labelMap = { production: t('dashboard.production'), staging: t('dashboard.staging'), development: t('dashboard.development') }
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

// ─── top errors bar ───
const topErrorsOption = computed(() => {
  const items = distributions.value.top_errors || []
  const names = items.map(i => i.exception_type).reverse()
  const counts = items.map(i => i.count).reverse()
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '8%', bottom: '3%', outerBounds: { contain: 'label' } },
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
    grid: { left: '3%', right: '8%', bottom: '3%', outerBounds: { contain: 'label' } },
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

// ─── data fetching ───
const refreshData = async () => {
  const params = {
    days: trendDays.value,
    hide_resolved: hideResolved.value ? 'true' : 'false',
  }
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
:deep(.el-table__row) {
  cursor: pointer;
}

@media (max-width: 768px) {
  :deep(.dashboard-table) {
    font-size: 13px;
  }

  :deep(.dashboard-table .el-table__cell) {
    padding: 8px 4px;
  }
}
</style>
