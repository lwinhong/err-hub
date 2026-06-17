<template>
  <div class="push-management-page">
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="28" height="28">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
          </svg>
        </div>
        <div>
          <h2 class="header-title">{{ t('pushManagement.title') }}</h2>
          <p class="header-subtitle">{{ t('pushManagement.subtitle') }}</p>
        </div>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="push-tabs">
      <el-tab-pane :label="t('pushManagement.providers')" name="providers">
        <PushProviders @changed="onDataChanged" />
      </el-tab-pane>
      <el-tab-pane :label="t('pushManagement.templates')" name="templates">
        <PushTemplates @changed="onDataChanged" />
      </el-tab-pane>
      <el-tab-pane :label="t('pushManagement.schedules')" name="schedules">
        <PushSchedules :refresh-key="refreshKey" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'
import { useI18n } from 'vue-i18n'
import PushProviders from './PushProviders.vue'
import PushTemplates from './PushTemplates.vue'
import PushSchedules from './PushSchedules.vue'

const { t } = useI18n()
const activeTab = ref('providers')
const refreshKey = ref(0)

const onDataChanged = () => {
  refreshKey.value++
}

provide('refreshKey', refreshKey)
</script>

<style scoped>
.push-management-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  padding: 24px;
  gap: 20px;
}

.page-header {
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
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  color: #fff;
  box-shadow: 0 4px 16px rgba(245, 158, 11, 0.35);
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

.push-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

:deep(.el-tabs__header) {
  flex-shrink: 0;
  margin: 0;
}

:deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
}

:deep(.el-tab-pane) {
  height: 100%;
  overflow-y: auto;
}
</style>
