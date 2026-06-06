<template>
  <div class="users">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        新建用户
      </el-button>
    </div>

    <el-card shadow="hover">
      <el-table :data="users" stripe v-loading="loading">
        <el-table-column prop="username" label="用户名" min-width="150" />
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_admin ? 'danger' : 'info'" size="small">
              {{ row.is_admin ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'warning'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="warning" @click="handleResetPassword(row)">重置密码</el-button>
            <el-button
              link
              :type="row.is_active ? 'warning' : 'success'"
              @click="handleToggleActive(row)"
            >
              {{ row.is_active ? '停用' : '启用' }}
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
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
      :title="editingUser ? '编辑用户' : '新建用户'"
      width="500px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="!!editingUser" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item v-if="!editingUser" label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="角色">
          <el-switch
            v-model="form.is_admin"
            active-text="管理员"
            inactive-text="普通用户"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="resetPwdDialogVisible"
      title="重置密码"
      width="420px"
      destroy-on-close
    >
      <el-form ref="resetPwdFormRef" :model="resetPwdForm" :rules="resetPwdRules" label-width="80px">
        <el-form-item label="新密码" prop="password">
          <el-input v-model="resetPwdForm.password" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetPwdDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="resetPwdSubmitting" @click="handleResetPasswordSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUsers, createUser, updateUser, resetUserPassword, deleteUser } from '../api/users'

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
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const resetPwdRules = {
  password: [{ required: true, message: '请输入新密码', trigger: 'blur' }]
}

const formatTime = (t) => {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
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
        ElMessage.success('用户已更新')
      } else {
        await createUser({
          username: form.username,
          password: form.password,
          is_admin: form.is_admin
        })
        ElMessage.success('用户已创建')
      }
      dialogVisible.value = false
      fetchUsers()
    } catch (err) {
      ElMessage.error(err.response?.data?.error || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleToggleActive = async (row) => {
  const action = row.is_active ? '停用' : '启用'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 "${row.username}" 吗？`, `${action}确认`, {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await updateUser(row.id, { is_active: !row.is_active })
    ElMessage.success(`用户已${action}`)
    fetchUsers()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.response?.data?.error || '操作失败')
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
      ElMessage.success('密码已重置')
      resetPwdDialogVisible.value = false
    } catch (err) {
      ElMessage.error(err.response?.data?.error || '重置失败')
    } finally {
      resetPwdSubmitting.value = false
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteUser(row.id)
      ElMessage.success('用户已删除')
      fetchUsers()
    } catch (err) {
      ElMessage.error(err.response?.data?.error || '删除失败')
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
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: var(--el-text-color-primary);
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
