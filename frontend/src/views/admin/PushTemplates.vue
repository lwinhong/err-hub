<template>
  <div class="push-templates-content">
    <div class="content-header">
      <el-button type="primary" @click="openDialog()">
        <el-icon>
          <Plus />
        </el-icon>
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
                  {{ tpl.template_type === 'error_report' ? t('pushTemplates.errorReport') :
                    t('pushTemplates.customSql') }}
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

    <el-dialog v-model="dialogVisible" :title="editingTemplate ? t('pushTemplates.edit') : t('pushTemplates.add')"
      width="700px" destroy-on-close>
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
            <el-select v-model="form.project_id" clearable :placeholder="t('pushTemplates.allProjects')"
              style="width: 100%">
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
            <el-input v-model="columnMappingJson" type="textarea" :rows="3"
              placeholder='{"col1": "列名1", "col2": "列名2"}' />
          </el-form-item>
        </template>

        <el-form-item :label="t('pushTemplates.subject')">
          <el-input v-model="form.subject" placeholder="{{project_name}} - Error Report" />
        </el-form-item>
        <el-form-item :label="t('pushTemplates.bodyTemplate')" required>
          <div class="template-helpers">
            <div class="helper-variables">
              <span class="helper-label">{{ t('pushTemplates.availableVars') }}:</span>
              <template v-if="form.template_type === 'error_report'">
                <el-tag v-for="(item, key) in errorReportVars" :key="key" size="small" type="info" class="var-tag"
                  :title="item.desc" @click="insertVar(key)" v-text="item.label" />
              </template>
              <template v-else>
                <el-tag v-for="(item, key) in customSqlVars" :key="key" size="small" type="info" class="var-tag"
                  :title="item.desc" @click="insertVar(key)" v-text="item.label" />
              </template>
            </div>
            <el-input ref="bodyTemplateRef" v-model="form.body_template" type="textarea" :rows="10" />
            <el-button size="small" type="primary" link @click="insertSample">
              {{ t('pushTemplates.insertSample') }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">
          {{ t('common.save') }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="previewVisible" :title="t('pushTemplates.previewTitle')" width="700px">
      <div class="preview-subject" v-if="previewData.subject">
        <strong>Subject:</strong> {{ previewData.subject }}
      </div>
      <div class="preview-content" v-html="previewData.content"></div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
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
const bodyTemplateRef = ref(null)
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
    } catch { }
  },
})

const ERROR_REPORT_SAMPLE = `<h2>{{project_name}} - 异常报告</h2>
<p>报告时间: {{time_range}}</p>
<table style="border-collapse:collapse;width:100%;margin:16px 0;">
  <tr style="background:#f5f5f5;">
    <td style="padding:12px;border:1px solid #eee;"><strong>异常总数</strong></td>
    <td style="padding:12px;border:1px solid #eee;">{{error_count}}</td>
    <td style="padding:12px;border:1px solid #eee;"><strong>新增异常</strong></td>
    <td style="padding:12px;border:1px solid #eee;">{{new_errors}}</td>
    <td style="padding:12px;border:1px solid #eee;"><strong>已解决</strong></td>
    <td style="padding:12px;border:1px solid #eee;">{{resolved_errors}}</td>
  </tr>
</table>
<h3>Top {{top_n}} 异常</h3>
{{error_list}}`

const CUSTOM_SQL_SAMPLE = `<h2>查询结果</h2>
<p>共 {{row_count}} 条记录</p>
{{table}}`

const errorReportVars = {
  project_name: { label: 'project_name', desc: '项目名称' },
  error_count: { label: 'error_count', desc: '异常总数' },
  new_errors: { label: 'new_errors', desc: '时间范围内新增的异常数' },
  resolved_errors: { label: 'resolved_errors', desc: '已解决的异常数' },
  error_list: { label: 'error_list', desc: 'Top N 异常列表（HTML表格）' },
  time_range: { label: 'time_range', desc: '统计时间范围，如 2024-01-01 00:00 ~ 2024-01-02 00:00' },
  top_n: { label: 'top_n', desc: '配置的 Top N 数量值' },
}

const customSqlVars = {
  table: { label: 'table', desc: 'SQL查询结果（HTML表格）' },
  row_count: { label: 'row_count', desc: '查询结果的行数' },
}

const insertVar = (varName) => {
  const textarea = bodyTemplateRef.value?.textarea
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = form.value.body_template
  const insertion = `{{${varName}}}`

  form.value.body_template = text.substring(0, start) + insertion + text.substring(end)

  nextTick(() => {
    textarea.focus()
    textarea.setSelectionRange(start + insertion.length, start + insertion.length)
  })
}

const insertSample = () => {
  if (form.value.template_type === 'error_report') {
    form.value.body_template = ERROR_REPORT_SAMPLE
  } else {
    form.value.body_template = CUSTOM_SQL_SAMPLE
  }
}

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
    const res = await getProjects({ per_page: 100 })
    projects.value = res.data.items || []
  } catch { }
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
.push-templates-content {}

.content-header {
  display: flex;
  justify-content: flex-end;
  margin: 16px 0;
}

.templates-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
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
  gap: 0px;
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
  max-height: 600px;
  overflow-y: auto;
}

.template-helpers {
  width: 100%;
}

.helper-variables {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding: 12px;
  background: linear-gradient(135deg, var(--el-fill-color-lighter) 0%, var(--el-fill-color-light) 100%);
  border: 1px dashed var(--el-border-color);
  border-radius: 8px;
}

.helper-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-secondary);
  margin-right: 4px;
}

.var-tag {
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-color: var(--el-color-primary-light-5);
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.var-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(var(--el-color-primary-rgb), 0.2);
  background: var(--el-color-primary-light-7);
  border-color: var(--el-color-primary);
}
</style>
