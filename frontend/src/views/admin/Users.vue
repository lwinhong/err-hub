<template>
  <div class="users-page">
    <!-- 标题区 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon">
          <el-icon :size="28"><User /></el-icon>
        </div>
        <div>
          <h2 class="header-title">{{ t('users.title') }}</h2>
          <p class="header-subtitle">{{ t('users.subtitle') }}</p>
        </div>
      </div>
      <button class="add-btn" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        <span>{{ t('users.createUser') }}</span>
      </button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card stat-total">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ total }}</span>
          <span class="stat-label">{{ t('users.totalUsers') }}</span>
        </div>
      </div>
      <div class="stat-card stat-admin">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ adminCount }}</span>
          <span class="stat-label">{{ t('users.admins') }}</span>
        </div>
      </div>
      <div class="stat-card stat-active">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ activeCount }}</span>
          <span class="stat-label">{{ t('users.activeUsers') }}</span>
        </div>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="users-table-wrap" v-loading="loading">
      <!-- 表头 -->
      <div class="table-header">
        <span class="col-user">{{ t('users.username') }}</span>
        <span class="col-role">{{ t('users.role') }}</span>
        <span class="col-status">{{ t('users.status') }}</span>
        <span class="col-time">{{ t('users.createdAt') }}</span>
        <span class="col-actions">{{ t('users.actions') }}</span>
      </div>
      <!-- 行 -->
      <div v-for="row in users" :key="row.id" class="table-row">
        <div class="col-user">
          <div class="user-avatar" :class="row.is_admin ? 'avatar-admin' : 'avatar-user'">
            {{ row.username.charAt(0).toUpperCase() }}
          </div>
          <span class="user-name">{{ row.username }}</span>
        </div>
        <div class="col-role">
          <span class="role-badge" :class="row.is_admin ? 'role-admin' : 'role-user'">
            {{ row.is_admin ? t('users.admin') : t('users.normalUser') }}
          </span>
        </div>
        <div class="col-status">
          <div class="status-dot" :class="row.is_active ? 'dot-active' : 'dot-inactive'"></div>
          <span>{{ row.is_active ? t('users.active') : t('users.inactive') }}</span>
        </div>
        <div class="col-time">{{ formatTime(row.created_at) }}</div>
        <div class="col-actions">
          <el-tooltip :content="t('users.edit')" placement="top" :show-after="300">
            <button class="action-btn action-edit" @click="openDialog(row)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
          </el-tooltip>
          <el-tooltip :content="t('users.resetPassword')" placement="top" :show-after="300">
            <button class="action-btn action-key" @click="handleResetPassword(row)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>
            </button>
          </el-tooltip>
          <el-tooltip :content="row.is_active ? t('users.disable') : t('users.enable')" placement="top" :show-after="300">
            <button class="action-btn" :class="row.is_active ? 'action-disable' : 'action-enable'" @click="handleToggleActive(row)">
              <svg v-if="row.is_active" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            </button>
          </el-tooltip>
          <el-tooltip :content="t('users.deleteUser')" placement="top" :show-after="300">
            <button class="action-btn action-delete" @click="handleDelete(row)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            </button>
          </el-tooltip>
        </div>
      </div>
      <!-- 空状态 -->
      <div v-if="!loading && users.length === 0" class="table-empty">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
          <line x1="17" y1="11" x2="23" y2="11"/>
        </svg>
        <span>{{ t('users.noData') }}</span>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrap">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchUsers"
        @current-change="fetchUsers"
      />
    </div>

    <!-- 新建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingUser ? t('users.editUser') : t('users.createUserTitle')" width="460px" destroy-on-close class="modern-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="dialog-form">
        <el-form-item :label="t('users.usernameLabel')" prop="username">
          <el-input v-model="form.username" :disabled="!!editingUser" :placeholder="t('users.usernamePlaceholder')" size="large" />
        </el-form-item>
        <el-form-item v-if="!editingUser" :label="t('users.passwordLabel')" prop="password">
          <el-input v-model="form.password" type="password" show-password :placeholder="t('users.passwordPlaceholder')" size="large" />
        </el-form-item>
        <el-form-item :label="t('users.role')">
          <div class="role-switch-row">
            <div class="role-option" :class="{ active: !form.is_admin }" @click="form.is_admin = false">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              {{ t('users.normalUser') }}
            </div>
            <div class="role-option" :class="{ active: form.is_admin }" @click="form.is_admin = true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              {{ t('users.admin') }}
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false" size="large">{{ t('users.cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit" size="large">
          {{ editingUser ? t('users.confirm') : t('users.createUser') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog v-model="resetPwdDialogVisible" :title="t('users.resetPwdTitle')" width="420px" destroy-on-close class="modern-dialog">
      <el-form ref="resetPwdFormRef" :model="resetPwdForm" :rules="resetPwdRules" label-position="top" class="dialog-form">
        <el-form-item :label="t('users.newPassword')" prop="password">
          <el-input v-model="resetPwdForm.password" type="password" show-password :placeholder="t('users.newPasswordPlaceholder')" size="large" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetPwdDialogVisible = false" size="large">{{ t('users.cancel') }}</el-button>
        <el-button type="primary" :loading="resetPwdSubmitting" @click="handleResetPasswordSubmit" size="large">
          {{ t('users.confirm') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus, User } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUsers, createUser, updateUser, resetUserPassword, deleteUser } from '../../api/users'
import { useSettingsStore } from '../../stores/settings'

const { t } = useI18n()
const settingsStore = useSettingsStore()

const loading = ref(false)
const users = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const dialogVisible = ref(false)
const submitting = ref(false)
const editingUser = ref(null)
const formRef = ref(null)

const resetPwdDialogVisible = ref(false)
const resetPwdSubmitting = ref(false)
const resetPwdFormRef = ref(null)
const resetPwdUserId = ref('')

const form = reactive({
  username: '',
  password: '',
  is_admin: false
})

const resetPwdForm = reactive({
  password: ''
})

const rules = {
  username: [{ required: true, message: t('users.usernameRequired'), trigger: 'blur' }],
  password: [{ required: true, message: t('users.passwordRequired'), trigger: 'blur' }]
}

const resetPwdRules = {
  password: [{ required: true, message: t('users.newPasswordRequired'), trigger: 'blur' }]
}

const adminCount = computed(() => users.value.filter(u => u.is_admin).length)
const activeCount = computed(() => users.value.filter(u => u.is_active).length)

const formatTime = (t) => {
  if (!t) return '-'
  return new Date(t).toLocaleString(localStorage.getItem('locale') === 'en' ? 'en-US' : 'zh-CN')
}

const openDialog = (user = null) => {
  editingUser.value = user
  form.username = user ? user.username : ''
  form.password = ''
  form.is_admin = user ? user.is_admin : false
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (editingUser.value) {
        await updateUser(editingUser.value.id, { is_admin: form.is_admin })
        ElMessage.success(t('users.userUpdated'))
      } else {
        await createUser({
          username: form.username,
          password: form.password,
          is_admin: form.is_admin
        })
        ElMessage.success(t('users.userCreated'))
      }
      dialogVisible.value = false
      fetchUsers()
    } catch (err) {
      ElMessage.error(err.response?.data?.error || t('users.operationFailed'))
    } finally {
      submitting.value = false
    }
  })
}

const handleToggleActive = async (row) => {
  const action = row.is_active ? t('users.disable') : t('users.enable')
  try {
    await ElMessageBox.confirm(t('users.toggleConfirm', { action, username: row.username }), t('users.toggleTitle', { action }), {
      confirmButtonText: t('users.confirm'),
      cancelButtonText: t('users.cancel'),
      type: 'warning'
    })
    await updateUser(row.id, { is_active: !row.is_active })
    ElMessage.success(t('users.userToggled', { action }))
    fetchUsers()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.response?.data?.error || t('users.operationFailed'))
    }
  }
}

const handleResetPassword = (row) => {
  resetPwdUserId.value = row.id
  resetPwdForm.password = ''
  resetPwdDialogVisible.value = true
}

const handleResetPasswordSubmit = async () => {
  if (!resetPwdFormRef.value) return
  await resetPwdFormRef.value.validate(async (valid) => {
    if (!valid) return
    resetPwdSubmitting.value = true
    try {
      await resetUserPassword(resetPwdUserId.value, resetPwdForm.password)
      ElMessage.success(t('users.passwordReset'))
      resetPwdDialogVisible.value = false
    } catch (err) {
      ElMessage.error(err.response?.data?.error || t('users.resetFailed'))
    } finally {
      resetPwdSubmitting.value = false
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(t('users.deleteConfirm', { username: row.username }), t('users.deleteTitle'), {
    confirmButtonText: t('users.confirm'),
    cancelButtonText: t('users.cancel'),
    type: 'warning'
  }).then(async () => {
    try {
      await deleteUser(row.id)
      ElMessage.success(t('users.userDeleted'))
      fetchUsers()
    } catch (err) {
      ElMessage.error(err.response?.data?.error || t('users.deleteFailed'))
    }
  }).catch(() => { })
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await getUsers({ page: page.value, per_page: pageSize.value })
    users.value = res.data.items || res.data
    total.value = res.data.total || users.value.length
  } catch { } finally {
    loading.value = false
  }
}

onMounted(() => {
  pageSize.value = settingsStore.defaultPageSize
  fetchUsers()
})

watch(() => settingsStore.defaultPageSize, (val) => {
  pageSize.value = val
  page.value = 1
  fetchUsers()
})
</script>

<style scoped>
.users-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 24px;
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
  background: linear-gradient(135deg, #8b5cf6, #a78bfa);
  color: #fff;
  box-shadow: 0 4px 16px rgba(139, 92, 246, 0.35);
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

.add-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #8b5cf6, #a78bfa);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(139, 92, 246, 0.35);
  transition: all 0.25s;
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(139, 92, 246, 0.45);
}

.add-btn:active {
  transform: translateY(0);
}

/* ── 统计卡片 ── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  flex-shrink: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  border-radius: 14px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  transition: box-shadow 0.3s, border-color 0.3s;
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

.stat-icon svg {
  width: 22px;
  height: 22px;
}

.stat-total .stat-icon {
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
}

.stat-admin .stat-icon {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.stat-active .stat-icon {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  line-height: 1;
  color: var(--el-text-color-primary);
  font-variant-numeric: tabular-nums;
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* ── 表格 ── */
.users-table-wrap {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  border-radius: 14px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
}

.table-header {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color-lighter);
  font-size: 12px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  position: sticky;
  top: 0;
  z-index: 1;
}

.table-row {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  transition: background 0.15s;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background: var(--el-fill-color-lighter);
}

.col-user {
  flex: 2;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.col-role {
  flex: 0 0 100px;
}

.col-status {
  flex: 0 0 100px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.col-time {
  flex: 1.5;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.col-actions {
  flex: 0 0 160px;
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: flex-end;
}

/* ── 用户头像 ── */
.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.avatar-admin {
  background: linear-gradient(135deg, #ef4444, #f87171);
}

.avatar-user {
  background: linear-gradient(135deg, #6366f1, #818cf8);
}

.user-name {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

/* ── 角色标签 ── */
.role-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 6px;
}

.role-admin {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.role-user {
  background: var(--el-fill-color);
  color: var(--el-text-color-secondary);
}

/* ── 状态点 ── */
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-active {
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.4);
}

.dot-inactive {
  background: var(--el-text-color-placeholder);
}

/* ── 操作按钮 ── */
.action-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  color: var(--el-text-color-secondary);
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.action-btn:hover {
  background: var(--el-fill-color);
}

.action-edit:hover { color: #3b82f6; }
.action-key:hover { color: #f59e0b; }
.action-enable:hover { color: #22c55e; }
.action-disable:hover { color: #ef4444; }
.action-delete:hover { color: #ef4444; background: rgba(239, 68, 68, 0.08); }

/* ── 空状态 ── */
.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px 20px;
  color: var(--el-text-color-placeholder);
}

/* ── 分页 ── */
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}

/* ── 对话框 ── */
.dialog-form :deep(.el-form-item__label) {
  font-weight: 600;
}

.role-switch-row {
  display: flex;
  gap: 10px;
  width: 100%;
}

.role-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 10px;
  border: 2px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-blank);
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-regular);
  cursor: pointer;
  transition: all 0.2s;
}

.role-option:hover {
  border-color: var(--el-border-color);
}

.role-option.active {
  border-color: #8b5cf6;
  background: rgba(139, 92, 246, 0.06);
  color: #8b5cf6;
  box-shadow: 0 2px 12px rgba(139, 92, 246, 0.15);
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .users-page {
    padding: 16px;
    gap: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .add-btn {
    width: 100%;
    justify-content: center;
  }

  .stats-row {
    grid-template-columns: 1fr;
  }

  .table-header,
  .table-row {
    padding: 10px 14px;
  }

  .col-time {
    display: none;
  }

  .col-actions {
    flex: 0 0 120px;
  }
}
</style>
