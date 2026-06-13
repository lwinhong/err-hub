<template>
  <div class="settings-page">
    <!-- 顶部标题区 -->
    <div class="settings-header">
      <div class="header-content">
        <div class="header-icon">
          <el-icon :size="28"><Setting /></el-icon>
        </div>
        <div>
          <h2 class="header-title">{{ t('settings.title') }}</h2>
          <p class="header-subtitle">{{ t('settings.subtitle') }}</p>
        </div>
      </div>
    </div>

    <el-skeleton :loading="loading" :rows="6" animated class="flex-1 min-h-0">
      <template #default>
        <div class="settings-grid">
          <!-- 数据保留天数 -->
          <div class="setting-card">
            <div class="card-accent accent-blue"></div>
            <div class="card-body">
              <div class="card-header-row">
                <div class="card-icon icon-blue">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                  </svg>
                </div>
                <div class="card-label">{{ t('settings.dataRetentionDays') }}</div>
                <div class="card-badge">{{ t('settings.unitDays') }}</div>
              </div>
              <div class="card-value-row">
                <el-input-number
                  v-model="form.data_retention_days"
                  :min="retentionMeta.min"
                  :max="retentionMeta.max"
                  :step="1"
                  controls-position="right"
                  @change="onFieldChange"
                  class="card-input-number"
                />
                <span class="card-unit">{{ t('settings.unitDays') }}</span>
              </div>
              <el-slider
                v-model="form.data_retention_days"
                :min="retentionMeta.min"
                :max="retentionMeta.max"
                :step="1"
                :show-tooltip="false"
                @change="onFieldChange"
                class="card-slider"
              />
              <div class="card-footer">
                <span class="card-hint">{{ t('settings.dataRetentionDaysHint', { default: retentionMeta.default }) }}</span>
              </div>
            </div>
          </div>

          <!-- 每页条数 -->
          <div class="setting-card">
            <div class="card-accent accent-green"></div>
            <div class="card-body">
              <div class="card-header-row">
                <div class="card-icon icon-green">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/>
                    <line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>
                  </svg>
                </div>
                <div class="card-label">{{ t('settings.defaultPageSize') }}</div>
                <div class="card-badge">{{ t('settings.unitItems') }}</div>
              </div>
              <div class="page-size-options">
                <button
                  v-for="size in [10, 20, 50]"
                  :key="size"
                  class="page-size-btn"
                  :class="{ active: form.default_page_size === size }"
                  @click="form.default_page_size = size; onFieldChange()"
                >
                  {{ size }}
                </button>
                <el-input-number
                  v-model="form.default_page_size"
                  :min="pageSizeMeta.min"
                  :max="pageSizeMeta.max"
                  :step="1"
                  controls-position="right"
                  @change="onFieldChange"
                  class="page-size-input"
                />
              </div>
              <div class="card-footer">
                <span class="card-hint">{{ t('settings.defaultPageSizeHint', { default: pageSizeMeta.default }) }}</span>
              </div>
            </div>
          </div>

          <!-- 显示用户列 -->
          <div class="setting-card">
            <div class="card-accent accent-purple"></div>
            <div class="card-body">
              <div class="card-header-row">
                <div class="card-icon icon-purple">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                </div>
                <div class="card-label">{{ t('settings.showUserColumn') }}</div>
                <div class="card-status" :class="form.show_user_column ? 'status-on' : 'status-off'">
                  {{ form.show_user_column ? 'ON' : 'OFF' }}
                </div>
              </div>
              <div class="toggle-row">
                <div class="toggle-track" :class="{ on: form.show_user_column }" @click="form.show_user_column = !form.show_user_column; onFieldChange()">
                  <div class="toggle-thumb"></div>
                </div>
              </div>
              <!-- 迷你预览 -->
              <div class="mini-preview">
                <div class="preview-table">
                  <div class="preview-row header">
                    <span>{{ t('projectErrors.exceptionType') }}</span>
                    <span v-if="form.show_user_column" class="fade-in">{{ t('projectErrors.user') }}</span>
                    <span>{{ t('projectErrors.severity') }}</span>
                  </div>
                  <div class="preview-row">
                    <span>TypeError</span>
                    <span v-if="form.show_user_column" class="fade-in">admin</span>
                    <span class="tag-err">error</span>
                  </div>
                </div>
              </div>
              <div class="card-footer">
                <span class="card-hint">{{ t('settings.showUserColumnHint') }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>
    </el-skeleton>

    <!-- 浮动操作栏 -->
    <transition name="slide-up">
      <div v-if="dirty" class="floating-bar">
        <button class="bar-btn bar-btn-reset" @click="handleReset">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
          </svg>
          {{ t('settings.reset') }}
        </button>
        <button class="bar-btn bar-btn-save" :disabled="saving" @click="doSave">
          <svg v-if="!saving" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
            <polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>
          </svg>
          <span v-if="saving" class="spinner"></span>
          {{ t('settings.save') }}
        </button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getSettings, updateSettings } from '../../api/settings'
import { useSettingsStore } from '../../stores/settings'

const { t } = useI18n()
const settingsStore = useSettingsStore()

const loading = ref(false)
const saving = ref(false)
const dirty = ref(false)

const retentionMeta = reactive({ min: 1, max: 3650, default: 90 })
const pageSizeMeta = reactive({ min: 10, max: 100, default: 20 })

const form = reactive({
  data_retention_days: 90,
  default_page_size: 20,
  show_user_column: false,
})

let savedValue = { data_retention_days: 90, default_page_size: 20, show_user_column: false }

const fetchSettings = async () => {
  loading.value = true
  try {
    const res = await getSettings()
    const data = res.data
    if (data.data_retention_days) {
      const s = data.data_retention_days
      const val = s.value ?? s.default ?? 90
      form.data_retention_days = val
      retentionMeta.min = s.min ?? 1
      retentionMeta.max = s.max ?? 3650
      retentionMeta.default = s.default ?? 90
    }
    if (data.default_page_size) {
      const s = data.default_page_size
      const val = s.value ?? s.default ?? 20
      form.default_page_size = val
      pageSizeMeta.min = s.min ?? 10
      pageSizeMeta.max = s.max ?? 100
      pageSizeMeta.default = s.default ?? 20
    }
    if (data.show_user_column) {
      const s = data.show_user_column
      form.show_user_column = s.value ?? s.default ?? false
    }
    savedValue = {
      data_retention_days: form.data_retention_days,
      default_page_size: form.default_page_size,
      show_user_column: form.show_user_column,
    }
  } catch {
    ElMessage.error(t('settings.loadFailed'))
  } finally {
    loading.value = false
  }
}

const onFieldChange = () => {
  dirty.value = form.data_retention_days !== savedValue.data_retention_days ||
    form.default_page_size !== savedValue.default_page_size ||
    form.show_user_column !== savedValue.show_user_column
}

const doSave = async () => {
  if (saving.value) return
  saving.value = true
  try {
    await updateSettings({
      data_retention_days: form.data_retention_days,
      default_page_size: form.default_page_size,
      show_user_column: form.show_user_column,
    })
    savedValue = {
      data_retention_days: form.data_retention_days,
      default_page_size: form.default_page_size,
      show_user_column: form.show_user_column,
    }
    dirty.value = false
    settingsStore.fetchSettings()
    ElMessage.success(t('settings.saveSuccess'))
  } catch (err) {
    ElMessage.error(err.response?.data?.error || t('settings.saveFailed'))
  } finally {
    saving.value = false
  }
}

const handleReset = () => {
  form.data_retention_days = savedValue.data_retention_days
  form.default_page_size = savedValue.default_page_size
  form.show_user_column = savedValue.show_user_column
  dirty.value = false
}

onMounted(() => {
  fetchSettings()
})
</script>

<style scoped>
.settings-page {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 24px;
  padding-bottom: 72px;
  gap: 24px;
}

/* ── 标题区 ── */
.settings-header {
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
  background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-primary-light-3));
  color: #fff;
  box-shadow: 0 4px 16px rgba(var(--el-color-primary-rgb), 0.35);
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

/* ── 卡片网格 ── */
.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-bottom: 80px;
}

.setting-card {
  position: relative;
  min-height: 240px;
  border-radius: 16px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  overflow: hidden;
  transition: box-shadow 0.3s, border-color 0.3s;
}

.setting-card:hover {
  border-color: var(--el-border-color);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.card-accent {
  height: 4px;
  width: 100%;
}

.accent-blue { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.accent-green { background: linear-gradient(90deg, #22c55e, #4ade80); }
.accent-purple { background: linear-gradient(90deg, #a855f7, #c084fc); }

.card-body {
  padding: 20px 24px 24px;
  display: flex;
  flex-direction: column;
}

.card-header-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-icon svg {
  width: 20px;
  height: 20px;
}

.icon-blue { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
.icon-green { background: rgba(34, 197, 94, 0.1); color: #22c55e; }
.icon-purple { background: rgba(168, 85, 247, 0.1); color: #a855f7; }

.card-label {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.card-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--el-fill-color-light);
  color: var(--el-text-color-secondary);
}

.card-status {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  padding: 2px 8px;
  border-radius: 6px;
}

.status-on {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.status-off {
  background: var(--el-fill-color-light);
  color: var(--el-text-color-secondary);
}

/* ── 数值输入 ── */
.card-value-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.card-input-number {
  width: 140px;
}

.card-input-number :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px var(--el-border-color-lighter);
}

.card-input-number :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--el-border-color);
}

.card-input-number :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--el-color-primary);
}

.card-input-number :deep(.el-input__inner) {
  font-size: 20px;
  font-weight: 700;
  text-align: center;
}

.card-unit {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

/* ── 滑块 ── */
.card-slider {
  margin: 0 -4px 16px;
}

.card-slider :deep(.el-slider__runway) {
  height: 6px;
  border-radius: 3px;
  background: var(--el-fill-color-darker);
}

.card-slider :deep(.el-slider__bar) {
  height: 6px;
  border-radius: 3px;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
}

.card-slider :deep(.el-slider__button-wrapper) {
  top: -14px;
}

.card-slider :deep(.el-slider__button) {
  width: 18px;
  height: 18px;
  border: 3px solid #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  transition: box-shadow 0.2s;
}

.card-slider :deep(.el-slider__button:hover) {
  box-shadow: 0 2px 12px rgba(59, 130, 246, 0.5);
}

/* ── 按钮组 ── */
.page-size-options {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.page-size-btn {
  flex: 1;
  height: 44px;
  border-radius: 10px;
  border: 2px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-blank);
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-regular);
  cursor: pointer;
  transition: all 0.2s;
}

.page-size-btn:hover {
  border-color: #22c55e;
  color: #22c55e;
}

.page-size-btn.active {
  border-color: #22c55e;
  background: rgba(34, 197, 94, 0.08);
  color: #22c55e;
  box-shadow: 0 2px 12px rgba(34, 197, 94, 0.2);
}

.page-size-input {
  width: 100px;
}

.page-size-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px var(--el-border-color-lighter);
}

.page-size-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--el-border-color);
}

.page-size-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--el-color-primary);
}

/* ── 自定义开关 ── */
.toggle-row {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.toggle-track {
  width: 56px;
  height: 30px;
  border-radius: 15px;
  background: var(--el-fill-color-darker);
  cursor: pointer;
  position: relative;
  transition: background 0.3s;
}

.toggle-track.on {
  background: linear-gradient(135deg, #a855f7, #c084fc);
  box-shadow: 0 2px 12px rgba(168, 85, 247, 0.35);
}

.toggle-thumb {
  width: 24px;
  height: 24px;
  border-radius: 12px;
  background: #fff;
  position: absolute;
  top: 3px;
  left: 3px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.toggle-track.on .toggle-thumb {
  transform: translateX(26px);
}

/* ── 迷你预览 ── */
.mini-preview {
  margin-bottom: 16px;
  border-radius: 10px;
  border: 1px solid var(--el-border-color-lighter);
  overflow: hidden;
  font-size: 12px;
}

.preview-table {
  width: 100%;
}

.preview-row {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  gap: 8px;
  color: var(--el-text-color-secondary);
}

.preview-row.header {
  background: var(--el-fill-color-light);
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.preview-row:not(.header) {
  border-top: 1px solid var(--el-border-color-lighter);
}

.preview-row span {
  flex-shrink: 0;
}

.preview-row span:first-child {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-err {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* ── 卡片底部 ── */
.card-footer {
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.card-hint {
  font-size: 12px;
  line-height: 1.5;
  color: var(--el-text-color-secondary);
}

/* ── 淡入动画 ── */
.fade-in {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-4px); }
  to { opacity: 1; transform: translateX(0); }
}

/* ── 浮动操作栏 ── */
.floating-bar {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: fit-content;
  display: flex;
  gap: 12px;
  padding: 12px 20px;
  border-radius: 14px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  z-index: 100;
}

.bar-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.bar-btn-reset {
  background: var(--el-fill-color-light);
  color: var(--el-text-color-regular);
}

.bar-btn-reset:hover {
  background: var(--el-fill-color);
}

.bar-btn-save {
  background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-primary-light-3));
  color: #fff;
  box-shadow: 0 2px 8px rgba(var(--el-color-primary-rgb), 0.3);
}

.bar-btn-save:hover {
  box-shadow: 0 4px 16px rgba(var(--el-color-primary-rgb), 0.4);
  transform: translateY(-1px);
}

.bar-btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── 滑入动画 ── */
.slide-up-enter-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(10px);
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .settings-page {
    padding: 16px;
    padding-bottom: 72px;
    gap: 16px;
  }

  .settings-grid {
    grid-template-columns: 1fr;
  }

  .slide-up-enter-from {
    transform: translateX(-50%) translateY(20px);
  }

  .slide-up-leave-to {
    transform: translateX(-50%) translateY(10px);
  }
}
</style>
