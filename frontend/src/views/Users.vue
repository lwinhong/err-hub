<template>
  <div class="users">
    <div class="page-header">
      <h2>{{ t('users.title') }}</h2>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        {{ t('users.createUser') }}
      </el-button>
    </div>

    <el-card shadow="hover" class="table-card">
      <div class="table-scroll">
        <el-table :data="users" stripe v-loading="loading" height="100%">
        <el-table-column prop="username" :label="t('users.username')" min-width="150" />
        <el-table-column :label="t('users.role')" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_admin ? 'danger' : 'info'" size="small">
              {{ row.is_admin ? t('users.admin') : t('users.normalUser') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('users.status')" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'warning'" size="small">
              {{ row.is_active ? t('users.active') : t('users.inactive') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" :label="t('users.createdAt')" width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column :label="t('users.actions')" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">{{ t('users.edit') }}</el-button>
            <el-button link type="warning" @click="handleResetPassword(row)">{{ t('users.resetPassword') }}</el-button>
            <el-button
              link
              :type="row.is_active ? 'warning' : 'success'"
              @click="handleToggleActive(row)"
            >
              {{ row.is_active ? t('users.disable') : t('users.enable') }}
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">{{ t('users.deleteUser') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      </div>
      <div class="pagination-wrapper">
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
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="editingUser ? t('users.editUser') : t('users.createUserTitle')"
      width="500px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item :label="t('users.usernameLabel')" prop="username">
          <el-input v-model="form.username" :disabled="!!editingUser" :placeholder="t('users.usernamePlaceholder')" />
        </el-form-item>
        <el-form-item v-if="!editingUser" :label="t('users.passwordLabel')" prop="password">
          <el-input v-model="form.password" type="password" show-password :placeholder="t('users.passwordPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('users.role')">
          <el-switch
            v-model="form.is_admin"
            :active-text="t('users.admin')"
            :inactive-text="t('users.normalUser')"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('users.cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">{{ t('users.confirm') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="resetPwdDialogVisible"
      :title="t('users.resetPwdTitle')"
      width="420px"
      destroy-on-close
    >
      <el-form ref="resetPwdFormRef" :model="resetPwdForm" :rules="resetPwdRules" label-width="80px">
        <el-form-item :label="t('users.newPassword')" prop="password">
          <el-input v-model="resetPwdForm.password" type="password" show-password :placeholder="t('users.newPasswordPlaceholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetPwdDialogVisible = false">{{ t('users.cancel') }}</el-button>
        <el-button type="primary" :loading="resetPwdSubmitting" @click="handleResetPasswordSubmit">{{ t('users.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUsers, createUser, updateUser, resetUserPassword, deleteUser } from '../api/users'

const { t } = useI18n()

const loading = ref(false)
const users = ref([])
const page = ref(1)
const pageSize = ref(10)
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
  }).catch(() => {})
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await getUsers({ page: page.value, per_page: pageSize.value })
    users.value = res.data.items || res.data
    total.value = res.data.total || users.value.length
  } catch {} finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.users {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: var(--el-text-color-primary);
}

.table-card {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.table-card :deep(.el-card__body) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.table-scroll {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .users {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .pagination-wrapper {
    justify-content: center;
  }

  .pagination-wrapper :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
