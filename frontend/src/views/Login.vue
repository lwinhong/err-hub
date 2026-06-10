<template>
  <div class="flex justify-center items-center min-h-screen p-5 max-sm:p-0 max-sm:items-start max-sm:pt-[15vh]" style="background-color: var(--el-bg-color-page)">
    <div class="w-[400px] max-w-full p-10 rounded-lg shadow-[0_2px_12px_rgba(0,0,0,0.1)] max-sm:p-6 max-sm:px-5 max-sm:shadow-none max-sm:rounded-none" style="background: var(--el-bg-color-overlay)">
      <div class="text-center mb-[30px]">
        <img src="/favicon.svg" alt="ErrHub" class="w-16 h-16 mx-auto mb-3" />
        <h1 class="text-[28px] max-sm:text-2xl font-bold m-0 mb-2" style="color: var(--el-color-primary)">ErrHub</h1>
        <p class="text-sm m-0" style="color: var(--el-text-color-secondary)">{{ t('login.subtitle') }}</p>
      </div>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item :label="t('login.username')" prop="username">
          <el-input
            v-model="form.username"
            :placeholder="t('login.usernamePlaceholder')"
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item :label="t('login.password')" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            :placeholder="t('login.passwordPlaceholder')"
            :prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="w-full"
            @click="handleLogin"
          >
            {{ t('login.submit') }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: t('login.usernameRequired'), trigger: 'blur' }],
  password: [{ required: true, message: t('login.passwordRequired'), trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await authStore.login(form.username, form.password)
      ElMessage.success(t('login.success'))
      router.push('/')
    } catch (err) {
      ElMessage.error(err.response?.data?.error || t('login.failed'))
    } finally {
      loading.value = false
    }
  })
}
</script>
