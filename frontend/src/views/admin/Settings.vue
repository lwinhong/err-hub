<template>
  <div class="p-5 h-full flex flex-col overflow-hidden box-border max-sm:p-3">
    <div class="flex justify-between items-center mb-5 shrink-0">
      <h2 class="m-0 text-xl" style="color: var(--el-text-color-primary)">{{ t('settings.title') }}</h2>
      <div class="flex">
        <el-button :disabled="!dirty" @click="handleReset">{{ t('settings.reset') }}</el-button>
        <el-button type="primary" :disabled="!dirty" :loading="saving" @click="doSave">
          {{ t('settings.save') }}
        </el-button>
      </div>
    </div>

    <el-card shadow="hover" class="flex-1 min-h-0 [&>.el-card__body]:h-full [&>.el-card__body]:box-border">
      <el-skeleton :loading="loading" :rows="4" animated>
        <template #default>
          <el-form ref="formRef" :model="form" :rules="rules" label-width="200px" label-position="right">
            <el-form-item :label="t('settings.dataRetentionDays')" prop="data_retention_days">
              <el-input-number
                v-model="form.data_retention_days"
                :min="retentionMeta.min"
                :max="retentionMeta.max"
                :step="1"
                controls-position="right"
                style="width: 200px"
                @change="onFieldChange"
              />
              <span class="ml-2" style="color: var(--el-text-color-regular)">{{ t('settings.unitDays') }}</span>
              <div class="text-xs leading-tight mt-1" style="color: var(--el-text-color-secondary)">
                {{ t('settings.dataRetentionDaysHint', { default: retentionMeta.default }) }}
              </div>
            </el-form-item>
          </el-form>
        </template>
      </el-skeleton>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { getSettings, updateSettings } from '../../api/settings'

const { t } = useI18n()

const loading = ref(false)
const saving = ref(false)
const dirty = ref(false)
const formRef = ref(null)

const retentionMeta = reactive({ min: 1, max: 3650, default: 90 })

const form = reactive({
  data_retention_days: 90,
})

// 记录上次已保存的值，用于判断 dirty
let savedValue = 90

const rules = {
  data_retention_days: [
    {
      required: true,
      message: t('settings.dataRetentionDaysRequired'),
      trigger: 'blur',
    },
  ],
}

const fetchSettings = async () => {
  loading.value = true
  try {
    const res = await getSettings()
    const data = res.data
    if (data.data_retention_days) {
      const s = data.data_retention_days
      const val = s.value ?? s.default ?? 90
      form.data_retention_days = val
      savedValue = val
      retentionMeta.min = s.min ?? 1
      retentionMeta.max = s.max ?? 3650
      retentionMeta.default = s.default ?? 90
    }
  } catch {
    ElMessage.error(t('settings.loadFailed'))
  } finally {
    loading.value = false
  }
}

const onFieldChange = () => {
  dirty.value = form.data_retention_days !== savedValue
}

const doSave = async () => {
  if (saving.value) return
  saving.value = true
  try {
    await updateSettings({ data_retention_days: form.data_retention_days })
    savedValue = form.data_retention_days
    dirty.value = false
    ElMessage.success(t('settings.saveSuccess'))
  } catch (err) {
    ElMessage.error(err.response?.data?.error || t('settings.saveFailed'))
  } finally {
    saving.value = false
  }
}

const handleReset = () => {
  form.data_retention_days = savedValue
  dirty.value = false
}

onMounted(() => {
  fetchSettings()
})
</script>

<style scoped>
</style>
