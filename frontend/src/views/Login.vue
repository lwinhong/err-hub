<template>
  <div class="login-page">
    <div class="login-left">
      <div class="login-left__content">
        <div class="login-left__brand">
          <img src="/favicon.svg" alt="ErrHub" class="login-left__logo" />
          <h1 class="login-left__title">ErrHub</h1>
        </div>
        <div class="login-left__hero">
          <div class="login-left__icon-row">
            <div class="login-left__icon-item">
              <div class="icon-circle icon-circle--red">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
              </div>
              <span>{{ t('login.feature1Title') }}</span>
            </div>
            <div class="login-left__icon-item">
              <div class="icon-circle icon-circle--blue">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
              </div>
              <span>{{ t('login.feature2Title') }}</span>
            </div>
            <div class="login-left__icon-item">
              <div class="icon-circle icon-circle--green">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              </div>
              <span>{{ t('login.feature3Title') }}</span>
            </div>
          </div>
        </div>
        <div class="login-left__features">
          <div class="feature-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            <span>{{ t('login.feature1Desc') }}</span>
          </div>
          <div class="feature-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <span>{{ t('login.feature2Desc') }}</span>
          </div>
          <div class="feature-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            <span>{{ t('login.feature3Desc') }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="login-right">
      <div class="login-settings">
        <el-dropdown trigger="click" @command="handleLangChange">
          <button class="settings-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="lang in languages"
                :key="lang.code"
                :command="lang.code"
                :class="{ 'is-active': locale === lang.code }"
              >
                {{ lang.label }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <button class="settings-btn" @click="handleToggleDark">
          <svg v-if="isDark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        </button>
      </div>
      <div class="login-form-wrapper">
        <div class="login-form-header">
          <h2>{{ t('login.welcome') }}</h2>
          <p>{{ t('login.subtitle') }}</p>
        </div>

        <div v-if="!showCaptcha">
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-position="top"
            @submit.prevent="handleLogin"
            class="login-form"
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
                class="w-full login-btn"
                @click="handleLogin"
              >
                {{ t('login.submit') }}
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <div v-else class="captcha-inline">
          <div class="captcha-inline__header">
            <button class="captcha-inline__back" @click="cancelCaptcha">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <span class="captcha-inline__title">{{ t('captcha.title') }}</span>
          </div>
          <CaptchaSlider ref="captchaRef" @verified="onCaptchaVerified" />
        </div>

        <div class="login-form-footer">
          <span>{{ t('login.footer') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useDark, useToggle } from '@vueuse/core'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { STORAGE_KEY, languages } from '../i18n'
import CaptchaSlider from '../components/CaptchaSlider.vue'

const router = useRouter()
const { t, locale } = useI18n()
const authStore = useAuthStore()
const isDark = useDark()
const toggleDark = useToggle(isDark)

const formRef = ref(null)
const captchaRef = ref(null)
const loading = ref(false)
const showCaptcha = ref(false)
const pendingLoginData = ref(null)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: t('login.usernameRequired'), trigger: 'blur' }],
  password: [{ required: true, message: t('login.passwordRequired'), trigger: 'blur' }]
}

const handleLangChange = (lang) => {
  locale.value = lang
  localStorage.setItem(STORAGE_KEY, lang)
}

const handleToggleDark = () => {
  const root = document.documentElement
  root.classList.add('theme-transition')
  toggleDark()
  setTimeout(() => {
    root.classList.remove('theme-transition')
  }, 350)
}

async function handleLogin() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  pendingLoginData.value = { username: form.username, password: form.password }
  showCaptcha.value = true
}

function cancelCaptcha() {
  showCaptcha.value = false
  pendingLoginData.value = null
}

function onCaptchaVerified(captchaId) {
  const data = pendingLoginData.value
  showCaptcha.value = false
  pendingLoginData.value = null
  doLogin(data.username, data.password, captchaId)
}

async function doLogin(username, password, captchaId) {
  loading.value = true
  try {
    await authStore.login(username, password, captchaId)
    ElMessage.success(t('login.success'))
    router.push('/')
  } catch (err) {
    ElMessage.error(err.response?.data?.error || t('login.failed'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  background: var(--el-bg-color-page);
}

.login-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 50%, #dbeafe 100%);
  position: relative;
  overflow: hidden;
}

.login-left::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 60%);
  animation: float 20s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, -30px); }
}

.login-left__content {
  position: relative;
  z-index: 1;
  max-width: 480px;
  color: #334155;
}

.login-left__brand {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 48px;
}

.login-left__logo {
  width: 56px;
  height: 56px;
}

.login-left__title {
  font-size: 36px;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.5px;
  color: #1e293b;
}

.login-left__hero {
  margin-bottom: 48px;
}

.login-left__icon-row {
  display: flex;
  gap: 24px;
}

.login-left__icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.login-left__icon-item span {
  font-size: 13px;
  color: #475569;
  font-weight: 500;
}

.icon-circle {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-circle svg {
  width: 28px;
  height: 28px;
}

.icon-circle--red {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.icon-circle--blue {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #2563eb;
}

.icon-circle--green {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #16a34a;
}

.login-left__features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.feature-item svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  color: #6366f1;
}

.feature-item span {
  font-size: 14px;
  color: #475569;
  line-height: 1.5;
}

.login-right {
  width: 480px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: var(--el-bg-color-overlay);
  position: relative;
}

.login-settings {
  position: absolute;
  top: 24px;
  right: 24px;
  display: flex;
  gap: 8px;
}

.settings-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-blank);
  border-radius: 8px;
  cursor: pointer;
  padding: 0;
  transition: all 0.2s;
}

.settings-btn:hover {
  background: var(--el-fill-color);
  border-color: var(--el-border-color);
}

.settings-btn svg {
  width: 18px;
  height: 18px;
  color: var(--el-text-color-regular);
}

.settings-btn:active {
  transform: scale(0.95);
}

:deep(.el-dropdown-menu__item.is-active) {
  color: var(--el-color-primary);
  font-weight: 600;
}

.login-form-wrapper {
  width: 100%;
  max-width: 360px;
}

.login-form-header {
  margin-bottom: 40px;
}

.login-form-header h2 {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: var(--el-text-color-primary);
}

.login-form-header p {
  font-size: 14px;
  margin: 0;
  color: var(--el-text-color-secondary);
}

.login-form {
  width: 100%;
}

.login-btn {
  height: 48px;
  font-size: 16px;
  margin-top: 8px;
}

.login-form-footer {
  margin-top: 32px;
  text-align: center;
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

.captcha-inline {
  padding: 20px 0;
}

.captcha-inline__header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.captcha-inline__back {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  cursor: pointer;
  padding: 0;
  transition: background 0.2s;
}

.captcha-inline__back:hover {
  background: var(--el-fill-color);
}

.captcha-inline__back svg {
  width: 16px;
  height: 16px;
  color: var(--el-text-color-regular);
}

.captcha-inline__title {
  font-size: 15px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

@media (max-width: 900px) {
  .login-page {
    flex-direction: column;
  }

  .login-left {
    padding: 40px 24px;
    min-height: auto;
  }

  .login-left__content {
    max-width: 100%;
  }

  .login-left__title {
    font-size: 28px;
  }

  .login-left__icon-row {
    gap: 16px;
  }

  .icon-circle {
    width: 52px;
    height: 52px;
  }

  .icon-circle svg {
    width: 24px;
    height: 24px;
  }

  .login-left__features {
    display: none;
  }

  .login-right {
    width: 100%;
    padding: 40px 24px;
  }

  .login-settings {
    top: 16px;
    right: 16px;
  }
}

:global(.dark) .login-left {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 50%, #1e1b4b 100%);
}

:global(.dark) .login-left::before {
  background: radial-gradient(circle, rgba(129,140,248,0.12) 0%, transparent 60%);
}

:global(.dark) .login-left__content {
  color: #e2e8f0;
}

:global(.dark) .login-left__title {
  color: #f1f5f9;
}

:global(.dark) .login-left__icon-item span {
  color: #94a3b8;
}

:global(.dark) .icon-circle--red {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
}

:global(.dark) .icon-circle--blue {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.3);
}

:global(.dark) .icon-circle--green {
  background: rgba(34, 197, 94, 0.15);
  border-color: rgba(34, 197, 94, 0.3);
}

:global(.dark) .feature-item {
  background: rgba(30, 41, 59, 0.8);
  border-color: rgba(51, 65, 85, 0.8);
}

:global(.dark) .feature-item svg {
  color: #818cf8;
}

:global(.dark) .feature-item span {
  color: #cbd5e1;
}
</style>
