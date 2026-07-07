<template>
  <div class="push-schedules-content">
    <div class="content-header">
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        {{ t('pushSchedules.add') }}
      </el-button>
    </div>

    <el-skeleton :loading="loading" :rows="5" animated>
      <template #default>
        <div v-if="schedules.length === 0" class="empty-state">
          <el-empty :description="t('pushSchedules.empty')" />
        </div>
        <div v-else class="schedules-list">
          <div v-for="schedule in schedules" :key="schedule.id" class="schedule-card">
            <div class="card-left">
              <div class="schedule-status" :class="schedule.is_active ? 'active' : 'inactive'">
                {{ schedule.is_active ? t('common.active') : t('common.inactive') }}
              </div>
              <div class="schedule-info">
                <h3 class="schedule-name">{{ schedule.name }}</h3>
                <div class="schedule-meta">
                  <span class="meta-item schedule-desc">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                      <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                    </svg>
                    {{ describeCron(schedule.cron_expression) }}
                  </span>
                  <span class="meta-item" v-if="schedule.provider">
                    {{ schedule.provider.name }}
                  </span>
                  <span class="meta-item" v-if="schedule.template">
                    {{ schedule.template.name }}
                  </span>
                </div>
                <div class="schedule-last-run" v-if="schedule.last_pushed_at">
                  {{ t('pushSchedules.lastRun') }}: {{ formatTime(schedule.last_pushed_at) }}
                </div>
              </div>
            </div>
            <div class="card-actions">
              <el-button size="small" @click="handleTrigger(schedule)" :loading="triggeringId === schedule.id">
                {{ t('pushSchedules.trigger') }}
              </el-button>
              <el-button size="small" @click="openDialog(schedule)">
                {{ t('common.edit') }}
              </el-button>
              <el-popconfirm :title="t('common.confirmDelete')" @confirm="handleDelete(schedule.id)">
                <template #reference>
                  <el-button size="small" type="danger">
                    {{ t('common.delete') }}
                  </el-button>
                </template>
              </el-popconfirm>
            </div>
          </div>
        </div>
      </template>
    </el-skeleton>

    <el-dialog
      v-model="dialogVisible"
      :title="editingSchedule ? t('pushSchedules.edit') : t('pushSchedules.add')"
      width="600px"
      destroy-on-close
    >
      <el-form :model="form" label-width="140px">
        <el-form-item :label="t('pushSchedules.name')" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item :label="t('pushSchedules.provider')" required>
          <el-select v-model="form.provider_id" style="width: 100%">
            <el-option
              v-for="p in providers"
              :key="p.id"
              :label="`${p.name} (${p.provider_type})`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pushSchedules.template')" required>
          <el-select v-model="form.template_id" style="width: 100%">
            <el-option
              v-for="tpl in templates"
              :key="tpl.id"
              :label="tpl.name"
              :value="tpl.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="t('pushSchedules.frequency')" required>
          <div class="frequency-config">
            <el-radio-group v-model="cronPreset" class="preset-group" @change="onPresetChange">
              <el-radio-button value="hourly">{{ t('pushSchedules.hourly') }}</el-radio-button>
              <el-radio-button value="daily">{{ t('pushSchedules.daily') }}</el-radio-button>
              <el-radio-button value="weekly">{{ t('pushSchedules.weekly') }}</el-radio-button>
              <el-radio-button value="monthly">{{ t('pushSchedules.monthly') }}</el-radio-button>
              <el-radio-button value="custom">{{ t('pushSchedules.custom') }}</el-radio-button>
            </el-radio-group>

            <div class="frequency-detail" v-if="cronPreset !== 'custom' && cronPreset !== 'hourly'">
              <span class="detail-label">{{ t('pushSchedules.atTime') }}</span>
              <el-time-picker
                v-model="cronTime"
                format="HH:mm"
                :clearable="false"
                @change="generateCron"
              />
            </div>

            <div class="frequency-detail" v-if="cronPreset === 'weekly'">
              <span class="detail-label">{{ t('pushSchedules.onDay') }}</span>
              <el-select v-model="cronWeekday" @change="generateCron" style="width: 140px">
                <el-option :label="t('pushSchedules.monday')" :value="1" />
                <el-option :label="t('pushSchedules.tuesday')" :value="2" />
                <el-option :label="t('pushSchedules.wednesday')" :value="3" />
                <el-option :label="t('pushSchedules.thursday')" :value="4" />
                <el-option :label="t('pushSchedules.friday')" :value="5" />
                <el-option :label="t('pushSchedules.saturday')" :value="6" />
                <el-option :label="t('pushSchedules.sunday')" :value="0" />
              </el-select>
            </div>

            <div class="frequency-detail" v-if="cronPreset === 'monthly'">
              <span class="detail-label">{{ t('pushSchedules.onDayOfMonth') }}</span>
              <el-input-number v-model="cronDay" :min="1" :max="28" @change="generateCron" />
              <span class="detail-suffix">{{ t('pushSchedules.daySuffix') }}</span>
            </div>

            <div v-if="cronPreset === 'custom'" class="custom-cron">
              <el-input v-model="form.cron_expression" placeholder="* * * * *" />
              <div class="cron-hint">{{ t('pushSchedules.cronHint') }}</div>
            </div>

            <div class="cron-preview">
              <el-icon><InfoFilled /></el-icon>
              {{ t('pushSchedules.willRun') }}: <strong>{{ describeCron(form.cron_expression) }}</strong>
            </div>
          </div>
        </el-form-item>

        <el-form-item :label="t('pushSchedules.active')">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">
          {{ t('common.save') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  getPushSchedules,
  createPushSchedule,
  updatePushSchedule,
  deletePushSchedule,
  triggerPushSchedule,
} from '../../api/pushSchedules'
import { getPushProviders } from '../../api/pushProviders'
import { getPushTemplates } from '../../api/pushTemplates'

const props = defineProps({
  refreshKey: { type: Number, default: 0 }
})

const { t } = useI18n()

const loading = ref(false)
const saving = ref(false)
const triggeringId = ref(null)
const schedules = ref([])
const providers = ref([])
const templates = ref([])
const dialogVisible = ref(false)
const editingSchedule = ref(null)

const cronPreset = ref('daily')
const cronTime = ref(new Date(2024, 0, 1, 9, 0))
const cronWeekday = ref(1)
const cronDay = ref(1)

const defaultForm = () => ({
  name: '',
  provider_id: null,
  template_id: null,
  cron_expression: '0 9 * * *',
  is_active: true,
})

const form = ref(defaultForm())

const WEEKDAY_NAMES = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

const describeCron = (cron) => {
  if (!cron) return ''
  const parts = cron.trim().split(/\s+/)
  if (parts.length !== 5) return cron

  const [min, hour, day, month, weekday] = parts

  if (min === '*' && hour === '*') return t('pushSchedules.descEveryMinute')
  if (min === '0' && hour === '*') return t('pushSchedules.descEveryHour')

  const timeStr = `${hour.padStart(2, '0')}:${min.padStart(2, '0')}`

  if (day === '*' && month === '*' && weekday === '*') {
    return t('pushSchedules.descEveryDayAt', { time: timeStr })
  }

  if (day === '*' && month === '*' && weekday !== '*') {
    const dayName = t(`pushSchedules.${WEEKDAY_NAMES[parseInt(weekday)]}`)
    return t('pushSchedules.descEveryWeekdayAt', { day: dayName, time: timeStr })
  }

  if (day !== '*' && month === '*' && weekday === '*') {
    return t('pushSchedules.descEveryMonthAt', { day: day, time: timeStr })
  }

  return cron
}

const detectPreset = (cron) => {
  if (!cron) return
  const parts = cron.trim().split(/\s+/)
  if (parts.length !== 5) {
    cronPreset.value = 'custom'
    return
  }

  const [min, hour, day, month, weekday] = parts

  if (min === '*' || (min !== '0' && min !== '*/1')) {
    cronPreset.value = 'custom'
    return
  }

  if (hour === '*') {
    cronPreset.value = 'hourly'
    return
  }

  if (day === '*' && month === '*' && weekday === '*') {
    cronPreset.value = 'daily'
    cronTime.value = new Date(2024, 0, 1, parseInt(hour) || 0, parseInt(min) || 0)
    return
  }

  if (day === '*' && month === '*' && weekday !== '*') {
    cronPreset.value = 'weekly'
    cronWeekday.value = parseInt(weekday)
    cronTime.value = new Date(2024, 0, 1, parseInt(hour) || 0, parseInt(min) || 0)
    return
  }

  if (day !== '*' && month === '*' && weekday === '*') {
    cronPreset.value = 'monthly'
    cronDay.value = parseInt(day) || 1
    cronTime.value = new Date(2024, 0, 1, parseInt(hour) || 0, parseInt(min) || 0)
    return
  }

  cronPreset.value = 'custom'
}

const onPresetChange = () => {
  if (cronPreset.value === 'hourly') {
    form.value.cron_expression = '0 * * * *'
  } else {
    generateCron()
  }
}

const generateCron = () => {
  if (cronPreset.value === 'custom') return

  const date = cronTime.value || new Date(2024, 0, 1, 9, 0)
  const min = date.getMinutes()
  const hour = date.getHours()

  if (cronPreset.value === 'hourly') {
    form.value.cron_expression = `0 * * * *`
  } else if (cronPreset.value === 'daily') {
    form.value.cron_expression = `${min} ${hour} * * *`
  } else if (cronPreset.value === 'weekly') {
    form.value.cron_expression = `${min} ${hour} * * ${cronWeekday.value}`
  } else if (cronPreset.value === 'monthly') {
    form.value.cron_expression = `${min} ${hour} ${cronDay.value} * *`
  }
}

const fetchSchedules = async () => {
  loading.value = true
  try {
    const res = await getPushSchedules()
    schedules.value = res.data
  } catch {
    ElMessage.error(t('pushSchedules.loadFailed'))
  } finally {
    loading.value = false
  }
}

const fetchProviders = async () => {
  try {
    const res = await getPushProviders()
    providers.value = res.data.filter(p => p.is_active)
  } catch {}
}

const fetchTemplates = async () => {
  try {
    const res = await getPushTemplates()
    templates.value = res.data
  } catch {}
}

const openDialog = (schedule = null) => {
  editingSchedule.value = schedule
  if (schedule) {
    form.value = {
      name: schedule.name,
      provider_id: schedule.provider_id,
      template_id: schedule.template_id,
      cron_expression: schedule.cron_expression,
      is_active: schedule.is_active,
    }
    detectPreset(schedule.cron_expression)
  } else {
    form.value = defaultForm()
    cronPreset.value = 'daily'
    cronTime.value = new Date(2024, 0, 1, 9, 0)
    cronWeekday.value = 1
    cronDay.value = 1
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.name.trim()) {
    ElMessage.warning(t('pushSchedules.nameRequired'))
    return
  }
  if (!form.value.provider_id) {
    ElMessage.warning(t('pushSchedules.providerRequired'))
    return
  }
  if (!form.value.template_id) {
    ElMessage.warning(t('pushSchedules.templateRequired'))
    return
  }
  if (!form.value.cron_expression.trim()) {
    ElMessage.warning(t('pushSchedules.cronRequired'))
    return
  }

  saving.value = true
  try {
    if (editingSchedule.value) {
      await updatePushSchedule(editingSchedule.value.id, form.value)
      ElMessage.success(t('common.saveSuccess'))
    } else {
      await createPushSchedule(form.value)
      ElMessage.success(t('common.createSuccess'))
    }
    dialogVisible.value = false
    fetchSchedules()
  } catch (err) {
    ElMessage.error(err.response?.data?.error || t('common.saveFailed'))
  } finally {
    saving.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await deletePushSchedule(id)
    ElMessage.success(t('common.deleteSuccess'))
    fetchSchedules()
  } catch (err) {
    ElMessage.error(err.response?.data?.error || t('common.deleteFailed'))
  }
}

const handleTrigger = async (schedule) => {
  triggeringId.value = schedule.id
  try {
    const res = await triggerPushSchedule(schedule.id)
    if (res.data.success) {
      ElMessage.success(t('pushSchedules.triggerSuccess'))
    } else {
      ElMessage.error(res.data.error || t('pushSchedules.triggerFailed'))
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.error || t('pushSchedules.triggerFailed'))
  } finally {
    triggeringId.value = null
  }
}

const formatTime = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleString()
}

onMounted(() => {
  fetchSchedules()
  fetchProviders()
  fetchTemplates()
})

watch(() => props.refreshKey, () => {
  fetchProviders()
  fetchTemplates()
})
</script>

<style scoped>
.push-schedules-content {
}

.content-header {
  display: flex;
  justify-content: flex-end;
  margin: 16px 0;
}

.schedules-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.schedule-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 12px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  padding: 20px 24px;
  transition: box-shadow 0.3s;
}

.schedule-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.card-left {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.schedule-status {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 6px;
  margin-top: 2px;
}

.schedule-status.active {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.schedule-status.inactive {
  background: var(--el-fill-color-light);
  color: var(--el-text-color-secondary);
}

.schedule-name {
  margin: 0 0 8px;
  font-size: 15px;
  font-weight: 600;
}

.schedule-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.meta-item.schedule-desc {
  color: var(--el-color-primary);
  font-weight: 500;
}

.schedule-last-run {
  margin-top: 8px;
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

.card-actions {
  display: flex;
  gap: 0px;
}

/* Frequency Config */
.frequency-config {
  width: 100%;
}

.preset-group {
  margin-bottom: 16px;
}

.frequency-detail {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: var(--el-fill-color-lighter);
  border-radius: 8px;
}

.detail-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
  white-space: nowrap;
}

.detail-suffix {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.custom-cron {
  margin-bottom: 12px;
}

.cron-hint {
  margin-top: 4px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.cron-preview {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  background: rgba(var(--el-color-primary-rgb), 0.05);
  border: 1px solid rgba(var(--el-color-primary-rgb), 0.2);
  border-radius: 8px;
  font-size: 13px;
  color: var(--el-color-primary);
}

.cron-preview strong {
  color: var(--el-text-color-primary);
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}
</style>
