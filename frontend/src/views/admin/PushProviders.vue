<template>
  <div class="push-providers-content">
    <div class="content-header">
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        {{ t('pushProviders.add') }}
      </el-button>
    </div>

    <el-skeleton :loading="loading" :rows="5" animated>
      <template #default>
        <div v-if="providers.length === 0" class="empty-state">
          <el-empty :description="t('pushProviders.empty')" />
        </div>
        <div v-else class="providers-grid">
          <div v-for="provider in providers" :key="provider.id" class="provider-card">
            <div class="card-header">
              <div class="provider-type-badge" :class="provider.provider_type">
                {{ provider.provider_type === 'webhook' ? 'Webhook' : 'PushPlus' }}
              </div>
              <div class="provider-status" :class="provider.is_active ? 'active' : 'inactive'">
                {{ provider.is_active ? t('common.active') : t('common.inactive') }}
              </div>
            </div>
            <h3 class="provider-name">{{ provider.name }}</h3>
            <div class="provider-info">
              <template v-if="provider.provider_type === 'webhook'">
                <span class="info-label">URL:</span>
                <span class="info-value url">{{ truncateUrl(provider.webhook_url) }}</span>
              </template>
              <template v-else>
                <span class="info-label">Channel:</span>
                <span class="info-value">{{ provider.pushplus_channel }}</span>
              </template>
            </div>
            <div class="card-actions">
              <el-button size="small" @click="testProvider(provider)" :loading="testingId === provider.id">
                {{ t('pushProviders.test') }}
              </el-button>
              <el-button size="small" @click="openDialog(provider)">
                {{ t('common.edit') }}
              </el-button>
              <el-popconfirm :title="t('common.confirmDelete')" @confirm="handleDelete(provider.id)">
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
      :title="editingProvider ? t('pushProviders.edit') : t('pushProviders.add')"
      width="600px"
      destroy-on-close
    >
      <el-form :model="form" label-width="140px">
        <el-form-item :label="t('pushProviders.name')" required>
          <el-input v-model="form.name" :placeholder="t('pushProviders.namePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('pushProviders.type')" required>
          <el-radio-group v-model="form.provider_type" :disabled="!!editingProvider">
            <el-radio value="webhook">Webhook</el-radio>
            <el-radio value="pushplus">PushPlus</el-radio>
          </el-radio-group>
        </el-form-item>

        <template v-if="form.provider_type === 'webhook'">
          <el-form-item label="URL" required>
            <el-input v-model="form.webhook_url" placeholder="https://your-service.com/webhook" />
          </el-form-item>
          <el-form-item :label="t('pushProviders.secret')">
            <el-input v-model="form.secret" placeholder="HMAC Secret (optional)" show-password />
          </el-form-item>
        </template>

        <template v-if="form.provider_type === 'pushplus'">
          <el-form-item label="Token" required>
            <el-input v-model="form.pushplus_token" placeholder="PushPlus Token" show-password />
          </el-form-item>
          <el-form-item :label="t('pushProviders.channel')">
            <el-select v-model="form.pushplus_channel" style="width: 100%">
              <el-option label="微信公众号" value="wechat" />
              <el-option label="企业微信应用" value="cp" />
              <el-option label="邮件" value="mail" />
              <el-option label="APP" value="app" />
              <el-option label="Webhook (第三方)" value="webhook" />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('pushProviders.template')">
            <el-select v-model="form.pushplus_template" style="width: 100%">
              <el-option label="HTML" value="html" />
              <el-option label="Markdown" value="markdown" />
              <el-option label="JSON" value="json" />
              <el-option label="纯文本" value="txt" />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('pushProviders.option')">
            <el-input v-model="form.pushplus_option" placeholder="渠道配置编码 (optional)" />
          </el-form-item>
        </template>

        <el-form-item :label="t('pushProviders.active')">
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
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  getPushProviders,
  createPushProvider,
  updatePushProvider,
  deletePushProvider,
  testPushProvider,
} from '../../api/pushProviders'

const emit = defineEmits(['changed'])
const { t } = useI18n()

const loading = ref(false)
const saving = ref(false)
const testingId = ref(null)
const providers = ref([])
const dialogVisible = ref(false)
const editingProvider = ref(null)

const defaultForm = () => ({
  name: '',
  provider_type: 'webhook',
  webhook_url: '',
  secret: '',
  pushplus_token: '',
  pushplus_channel: 'wechat',
  pushplus_template: 'html',
  pushplus_option: '',
  is_active: true,
})

const form = ref(defaultForm())

const fetchProviders = async () => {
  loading.value = true
  try {
    const res = await getPushProviders()
    providers.value = res.data
  } catch {
    ElMessage.error(t('pushProviders.loadFailed'))
  } finally {
    loading.value = false
  }
}

const openDialog = (provider = null) => {
  editingProvider.value = provider
  if (provider) {
    form.value = { ...provider }
  } else {
    form.value = defaultForm()
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.name.trim()) {
    ElMessage.warning(t('pushProviders.nameRequired'))
    return
  }
  if (form.value.provider_type === 'webhook' && !form.value.webhook_url.trim()) {
    ElMessage.warning(t('pushProviders.urlRequired'))
    return
  }
  if (form.value.provider_type === 'pushplus' && !form.value.pushplus_token.trim()) {
    ElMessage.warning(t('pushProviders.tokenRequired'))
    return
  }

  saving.value = true
  try {
    if (editingProvider.value) {
      await updatePushProvider(editingProvider.value.id, form.value)
      ElMessage.success(t('common.saveSuccess'))
    } else {
      await createPushProvider(form.value)
      ElMessage.success(t('common.createSuccess'))
    }
    dialogVisible.value = false
    fetchProviders()
    emit('changed')
  } catch (err) {
    ElMessage.error(err.response?.data?.error || t('common.saveFailed'))
  } finally {
    saving.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await deletePushProvider(id)
    ElMessage.success(t('common.deleteSuccess'))
    fetchProviders()
    emit('changed')
  } catch (err) {
    ElMessage.error(err.response?.data?.error || t('common.deleteFailed'))
  }
}

const testProvider = async (provider) => {
  testingId.value = provider.id
  try {
    const res = await testPushProvider(provider.id)
    if (res.data.success) {
      ElMessage.success(t('pushProviders.testSuccess'))
    } else {
      ElMessage.error(res.data.error || t('pushProviders.testFailed'))
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.error || t('pushProviders.testFailed'))
  } finally {
    testingId.value = null
  }
}

const truncateUrl = (url) => {
  if (!url) return ''
  return url.length > 40 ? url.substring(0, 40) + '...' : url
}

onMounted(fetchProviders)
</script>

<style scoped>
.push-providers-content {
}

.content-header {
  display: flex;
  justify-content: flex-end;
  margin: 16px 0;
}

.providers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.provider-card {
  border-radius: 16px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  padding: 24px;
  transition: box-shadow 0.3s;
}

.provider-card:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.provider-type-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 6px;
}

.provider-type-badge.webhook {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.provider-type-badge.pushplus {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.provider-status {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 6px;
}

.provider-status.active {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.provider-status.inactive {
  background: var(--el-fill-color-light);
  color: var(--el-text-color-secondary);
}

.provider-name {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 600;
}

.provider-info {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-bottom: 16px;
}

.info-label {
  font-weight: 500;
}

.info-value.url {
  font-family: monospace;
  font-size: 12px;
}

.card-actions {
  display: flex;
  gap: 0px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}
</style>
