<template>
  <div class="push-templates-content">
    <div class="content-header">
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        {{ t('pushTemplates.add') }}
      </el-button>
    </div>

    <el-skeleton :loading="loading" :rows="5" animated>
      <template #default>
        <div v-if="templates.length === 0" class="empty-state">
          <el-empty :description="t('pushTemplates.empty')" />
        </div>
        <div v-else class="templates-list">
          <div v-for="tpl in templates" :key="tpl.id" class="template-card">
            <div class="card-body">
              <div class="card-left">
                <div class="template-type-badge" :class="tpl.template_type">
                  {{ tpl.template_type === 'error_report' ? t('pushTemplates.errorReport') : t('pushTemplates.customSql') }}
                </div>
                <h3 class="template-name">{{ tpl.name }}</h3>
                <p class="template-subject">{{ tpl.subject || '(no subject)' }}</p>
                <div class="template-meta">
                  <span v-if="tpl.top_n">Top {{ tpl.top_n }}</span>
                  <span v-if="tpl.time_range_hours">{{ tpl.time_range_hours }}h</span>
                </div>
              </div>
              <div class="card-actions">
                <el-button size="small" @click="handlePreview(tpl)">
                  {{ t('pushTemplates.preview') }}
                </el-button>
                <el-button size="small" @click="openDialog(tpl)">
                  {{ t('common.edit') }}
                </el-button>
                <el-popconfirm :title="t('common.confirmDelete')" @confirm="handleDelete(tpl.id)">
                  <template #reference>
                    <el-button size="small" type="danger">
                      {{ t('common.delete') }}
                    </el-button>
                  </template>
                </el-popconfirm>
              </div>
            </div>
          </div>
        </div>
      </template>
    </el-skeleton>

    <el-dialog
      v-model="dialogVisible"
      :title="editingTemplate ? t('pushTemplates.edit') : t('pushTemplates.add')"
      width="700px"
      destroy-on-close
    >
      <el-form :model="form" label-width="120px">
        <el-form-item :label="t('pushTemplates.name')" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item :label="t('pushTemplates.type')" required>
          <el-radio-group v-model="form.template_type">
            <el-radio value="error_report">{{ t('pushTemplates.errorReport') }}</el-radio>
            <el-radio value="custom_sql">{{ t('pushTemplates.customSql') }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <template v-if="form.template_type === 'error_report'">
          <el-form-item :label="t('pushTemplates.project')">
            <el-select v-model="form.project_id" clearable :placeholder="t('pushTemplates.allProjects')" style="width: 100%">
              <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('pushTemplates.topN')">
            <el-input-number v-model="form.top_n" :min="1" :max="50" />
          </el-form-item>
          <el-form-item :label="t('pushTemplates.timeRange')">
            <el-input-number v-model="form.time_range_hours" :min="1" :max="720" />
            <span style="margin-left: 8px; color: var(--el-text-color-secondary);">hours</span>
          </el-form-item>
        </template>

        <template v-if="form.template_type === 'custom_sql'">
          <el-form-item label="SQL" required>
            <el-input v-model="form.sql_query" type="textarea" :rows="4" placeholder="SELECT ..." />
          </el-form-item>
          <el-form-item :label="t('pushTemplates.columnMapping')">
            <el-input v-model="columnMappingJson" type="textarea" :rows="3" placeholder='{"col1": "列名1", "col2": "列名2"}' />
          </el-form-item>
        </template>

        <el-form-item :label="t('pushTemplates.subject')">
          <el-input v-model="form.subject" placeholder="{{project_name}} - Error Report" />
        </el-form-item>
        <el-form-item :label="t('pushTemplates.bodyTemplate')" required>
          <el-input v-model="form.body_template" type="textarea" :rows="10" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">
          {{ t('common.save') }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="previewVisible"
      :title="t('pushTemplates.previewTitle')"
      width="700px"
    >
      <div class="preview-subject" v-if="previewData.subject">
        <strong>Subject:</strong> {{ previewData.subject }}
      </div>
      <div class="preview-content" v-html="previewData.content"></div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  getPushTemplates,
  createPushTemplate,
  updatePushTemplate,
  deletePushTemplate,
  previewPushTemplate,
} from '../../api/pushTemplates'
import { getProjects } from '../../api/projects'

const emit = defineEmits(['changed'])
const { t } = useI18n()

const loading = ref(false)
const saving = ref(false)
const templates = ref([])
const projects = ref([])
const dialogVisible = ref(false)
const previewVisible = ref(false)
const editingTemplate = ref(null)
const previewData = ref({ subject: '', content: '' })

const defaultForm = () => ({
  name: '',
  template_type: 'error_report',
  project_id: null,
  top_n: 10,
  time_range_hours: 24,
  sql_query: '',
  column_mapping: null,
  subject: '',
  body_template: '',
})

const form = ref(defaultForm())

const columnMappingJson = computed({
  get: () => form.value.column_mapping ? JSON.stringify(form.value.column_mapping, null, 2) : '',
  set: (val) => {
    try {
      form.value.column_mapping = val.trim() ? JSON.parse(val) : null
    } catch {}
  },
})

const fetchTemplates = async () => {
  loading.value = true
  try {
    const res = await getPushTemplates()
    templates.value = res.data
  } catch {
    ElMessage.error(t('pushTemplates.loadFailed'))
  } finally {
    loading.value = false
  }
}

const fetchProjects = async () => {
  try {
    const res = await getProjects()
    projects.value = res.data
  } catch {}
}

const openDialog = (tpl = null) => {
  editingTemplate.value = tpl
  if (tpl) {
    form.value = { ...tpl }
  } else {
    form.value = defaultForm()
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.name.trim() || !form.value.body_template.trim()) {
    ElMessage.warning(t('pushTemplates.nameAndBodyRequired'))
    return
  }
  if (form.value.template_type === 'custom_sql' && !form.value.sql_query.trim()) {
    ElMessage.warning(t('pushTemplates.sqlRequired'))
    return
  }

  saving.value = true
  try {
    if (editingTemplate.value) {
      await updatePushTemplate(editingTemplate.value.id, form.value)
      ElMessage.success(t('common.saveSuccess'))
    } else {
      await createPushTemplate(form.value)
      ElMessage.success(t('common.createSuccess'))
    }
    dialogVisible.value = false
    fetchTemplates()
    emit('changed')
  } catch (err) {
    ElMessage.error(err.response?.data?.error || t('common.saveFailed'))
  } finally {
    saving.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await deletePushTemplate(id)
    ElMessage.success(t('common.deleteSuccess'))
    fetchTemplates()
    emit('changed')
  } catch (err) {
    ElMessage.error(err.response?.data?.error || t('common.deleteFailed'))
  }
}

const handlePreview = async (tpl) => {
  try {
    const res = await previewPushTemplate(tpl.id)
    previewData.value = res.data
    previewVisible.value = true
  } catch (err) {
    ElMessage.error(err.response?.data?.error || t('pushTemplates.previewFailed'))
  }
}

onMounted(() => {
  fetchTemplates()
  fetchProjects()
})
</script>

<style scoped>
.push-templates-content {
}

.content-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.templates-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.template-card {
  border-radius: 12px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  transition: box-shadow 0.3s;
}

.template-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.card-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
}

.card-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.template-type-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 6px;
}

.template-type-badge.error_report {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.template-type-badge.custom_sql {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.template-name {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}

.template-subject {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.template-meta {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.template-meta span {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--el-fill-color-light);
  color: var(--el-text-color-secondary);
}

.card-actions {
  display: flex;
  gap: 8px;
}

.preview-subject {
  margin-bottom: 16px;
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
}

.preview-content {
  padding: 20px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  max-height: 400px;
  overflow-y: auto;
}
</style>
