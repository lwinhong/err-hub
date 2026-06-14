<template>
  <div class="login-page">
    <!-- 左侧品牌区 -->
    <div class="login-left">
      <div class="login-left__bg">
        <div class="bg-orb bg-orb-1"></div>
        <div class="bg-orb bg-orb-2"></div>
        <div class="bg-orb bg-orb-3"></div>
        <div class="bg-grid"></div>
      </div>
      <div class="login-left__content">
        <div class="login-left__brand">
          <div class="brand-logo">
            <img src="/favicon.svg" alt="ErrHub" class="brand-logo__img" />
          </div>
          <h1 class="brand-title">ErrHub</h1>
        </div>

        <p class="brand-tagline">{{ t('login.subtitle') }}</p>

        <div class="feature-cards">
          <div class="feature-card card-red">
            <div class="feature-card__icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            </div>
            <div class="feature-card__text">
              <span class="feature-card__title">{{ t('login.feature1Title') }}</span>
              <span class="feature-card__desc">{{ t('login.feature1Desc') }}</span>
            </div>
          </div>
          <div class="feature-card card-blue">
            <div class="feature-card__icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            </div>
            <div class="feature-card__text">
              <span class="feature-card__title">{{ t('login.feature2Title') }}</span>
              <span class="feature-card__desc">{{ t('login.feature2Desc') }}</span>
            </div>
          </div>
          <div class="feature-card card-green">
            <div class="feature-card__icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            </div>
            <div class="feature-card__text">
              <span class="feature-card__title">{{ t('login.feature3Title') }}</span>
              <span class="feature-card__desc">{{ t('login.feature3Desc') }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录区 -->
    <div class="login-right">
      <!-- 设置按钮 -->
      <div class="login-settings">
        <el-dropdown trigger="click" @command="handleLangChange">
          <button class="settings-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-for="lang in languages" :key="lang.code" :command="lang.code" :class="{ 'is-active': locale === lang.code }">
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
        <!-- Logo (移动端) -->
        <div class="mobile-brand">
          <img src="/favicon.svg" alt="ErrHub" class="mobile-brand__img" />
          <span class="mobile-brand__name">ErrHub</span>
        </div>

        <div class="login-form-header">
          <h2>{{ t('login.welcome') }}</h2>
          <p>{{ t('login.subtitle') }}</p>
        </div>

        <!-- 登录表单 -->
        <div v-if="!showCaptcha" class="login-form-body">
          <div class="input-group">
            <label class="input-label">{{ t('login.username') }}</label>
            <div class="input-wrapper">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="input-icon"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <input
                v-model="form.username"
                :placeholder="t('login.usernamePlaceholder')"
                class="login-input"
                @keyup.enter="handleLogin"
              />
            </div>
            <span v-if="errors.username" class="input-error">{{ errors.username }}</span>
          </div>

          <div class="input-group">
            <label class="input-label">{{ t('login.password') }}</label>
            <div class="input-wrapper">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="input-icon"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              <input
                v-model="form.password"
                :type="showPwd ? 'text' : 'password'"
                :placeholder="t('login.passwordPlaceholder')"
                class="login-input"
                @keyup.enter="handleLogin"
              />
              <button class="pwd-toggle" @click="showPwd = !showPwd" type="button">
                <svg v-if="!showPwd" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              </button>
            </div>
            <span v-if="errors.password" class="input-error">{{ errors.password }}</span>
          </div>

          <button class="login-btn" :class="{ loading }" :disabled="loading" @click="handleLogin">
            <span v-if="loading" class="btn-spinner"></span>
            <span v-else>{{ t('login.submit') }}</span>
          </button>
        </div>

        <!-- 验证码 -->
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
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { STORAGE_KEY, languages } from '../i18n'
import CaptchaSlider from '../components/CaptchaSlider.vue'

const router = useRouter()
const { t, locale } = useI18n()
const authStore = useAuthStore()
const isDark = useDark()
const toggleDark = useToggle(isDark)

const captchaRef = ref(null)
const loading = ref(false)
const showCaptcha = ref(false)
const showPwd = ref(false)
const pendingLoginData = ref(null)

const form = reactive({
  username: '',
  password: ''
})

const errors = reactive({
  username: '',
  password: ''
})

const validate = () => {
  errors.username = form.username ? '' : t('login.usernameRequired')
  errors.password = form.password ? '' : t('login.passwordRequired')
  return !errors.username && !errors.password
}

const handleLangChange = (lang) => {
  locale.value = lang
  localStorage.setItem(STORAGE_KEY, lang)
}

const handleToggleDark = () => {
  const root = document.documentElement
  root.classList.add('theme-transition')
  toggleDark()
  setTimeout(() => root.classList.remove('theme-transition'), 350)
}

async function handleLogin() {
  if (!validate()) return
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
  if (data) {
    doLogin(data.username, data.password, captchaId)
  }
}

async function doLogin(username, password, captchaId) {
  loading.value = true
  try {
    await authStore.login(username, password, captchaId)
    ElMessage.success(t('login.success'))
    router.push('/')
  } catch (err) {
    const status = err.response?.status
    const errorMsg = err.response?.data?.error || ''
    if (status === 403 && errorMsg.includes('locked')) {
      const remaining = err.response?.data?.remaining_seconds
      if (remaining > 0) {
        ElMessage.error(t('login.accountLocked', { seconds: remaining }))
      } else {
        ElMessage.error(t('login.accountLockedNoTime'))
      }
    } else {
      ElMessage.error(errorMsg || t('login.failed'))
    }
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

/* ── 左侧品牌区 ── */
.login-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
}

.login-left__bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
}

.bg-orb-1 {
  width: 400px;
  height: 400px;
  background: #6366f1;
  top: -100px;
  right: -100px;
  animation: float1 15s ease-in-out infinite;
}

.bg-orb-2 {
  width: 300px;
  height: 300px;
  background: #ec4899;
  bottom: -50px;
  left: -50px;
  animation: float2 18s ease-in-out infinite;
}

.bg-orb-3 {
  width: 200px;
  height: 200px;
  background: #22d3ee;
  top: 50%;
  left: 50%;
  animation: float3 12s ease-in-out infinite;
}

@keyframes float1 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-40px, 40px); }
}

@keyframes float2 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, -30px); }
}

@keyframes float3 {
  0%, 100% { transform: translate(-50%, -50%); }
  50% { transform: translate(-50%, -50%) scale(1.2); }
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 40px 40px;
}

.login-left__content {
  position: relative;
  z-index: 1;
  max-width: 460px;
}

.login-left__brand {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.brand-logo {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.15);
}

.brand-logo__img {
  width: 36px;
  height: 36px;
  display: block;
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  margin: 0;
  color: #fff;
  letter-spacing: -0.5px;
}

.brand-tagline {
  font-size: 16px;
  color: rgba(255,255,255,0.6);
  margin: 0 0 48px;
  line-height: 1.6;
}

/* ── 特性卡片 ── */
.feature-cards {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.feature-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 14px;
  background: rgba(255,255,255,0.06);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.08);
  transition: all 0.3s;
}

.feature-card:hover {
  background: rgba(255,255,255,0.1);
  border-color: rgba(255,255,255,0.15);
  transform: translateX(4px);
}

.feature-card__icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-card__icon svg {
  width: 22px;
  height: 22px;
}

.card-red .feature-card__icon { background: rgba(239, 68, 68, 0.2); color: #f87171; }
.card-blue .feature-card__icon { background: rgba(99, 102, 241, 0.2); color: #818cf8; }
.card-green .feature-card__icon { background: rgba(34, 197, 94, 0.2); color: #4ade80; }

.feature-card__text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.feature-card__title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.feature-card__desc {
  font-size: 12px;
  color: rgba(255,255,255,0.5);
  line-height: 1.4;
}

/* ── 右侧登录区 ── */
.login-right {
  width: 480px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: #ffffff;
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
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 10px;
  cursor: pointer;
  padding: 0;
  transition: all 0.2s;
  color: #64748b;
}

.settings-btn:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #6366f1;
}

.settings-btn svg {
  width: 18px;
  height: 18px;
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

/* ── 移动端品牌 ── */
.mobile-brand {
  display: none;
  align-items: center;
  gap: 12px;
  margin-bottom: 32px;
}

.mobile-brand__img {
  width: 40px;
  height: 40px;
}

.mobile-brand__name {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.login-form-header {
  margin-bottom: 36px;
  text-align: center;
}

.login-form-header h2 {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px;
  color: #1e293b;
}

.login-form-header p {
  font-size: 14px;
  margin: 0;
  color: #94a3b8;
}

/* ── 输入框 ── */
.input-group {
  margin-bottom: 20px;
}

.input-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 8px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  height: 48px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1.5px solid #e2e8f0;
  background: #f8fafc;
  transition: all 0.2s;
}

.input-wrapper:focus-within {
  border-color: #6366f1;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.input-icon {
  width: 18px;
  height: 18px;
  color: #94a3b8;
  flex-shrink: 0;
}

.login-input {
  flex: 1;
  height: 100%;
  border: none;
  outline: none;
  background: transparent;
  font-size: 15px;
  color: #1e293b;
  padding: 0 12px;
}

.login-input::placeholder {
  color: #cbd5e1;
}

.pwd-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 6px;
  color: #94a3b8;
  transition: all 0.2s;
  flex-shrink: 0;
}

.pwd-toggle:hover {
  color: #64748b;
  background: #f1f5f9;
}

.input-error {
  display: block;
  font-size: 12px;
  color: #ef4444;
  margin-top: 6px;
}

/* ── 登录按钮 ── */
.login-btn {
  width: 100%;
  height: 48px;
  margin-top: 8px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1, #818cf8);
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.25s;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(99, 102, 241, 0.4);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── 验证码 ── */
.captcha-inline {
  padding: 20px 0;
}

.captcha-inline__header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.captcha-inline__back {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  padding: 0;
  transition: all 0.2s;
  color: #64748b;
}

.captcha-inline__back:hover {
  border-color: #cbd5e1;
  color: #6366f1;
}

.captcha-inline__back svg {
  width: 16px;
  height: 16px;
}

.captcha-inline__title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

/* ── 底部 ── */
.login-form-footer {
  margin-top: 32px;
  text-align: center;
  font-size: 12px;
  color: #94a3b8;
}

/* ── 响应式 ── */
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

  .brand-title {
    font-size: 28px;
  }

  .brand-tagline {
    margin-bottom: 24px;
  }

  .feature-cards {
    gap: 10px;
  }

  .feature-card {
    padding: 12px 16px;
  }

  .login-right {
    width: 100%;
    padding: 40px 24px;
  }

  .mobile-brand {
    display: flex;
  }

  .login-settings {
    top: 16px;
    right: 16px;
  }
}

/* ── 暗色主题 ── */
:deep(html.dark) .login-left {
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%) !important;
}

:deep(html.dark) .bg-orb-1 { background: #818cf8; }
:deep(html.dark) .bg-orb-2 { background: #f472b6; }
:deep(html.dark) .bg-orb-3 { background: #22d3ee; }

:deep(html.dark) .login-right {
  background: #1a1a2e !important;
}

:deep(html.dark) .login-form-header h2 { color: #f1f5f9 !important; }
:deep(html.dark) .login-form-header p { color: #94a3b8 !important; }
:deep(html.dark) .input-label { color: #e2e8f0 !important; }

:deep(html.dark) .input-wrapper {
  background: #16213e !important;
  border-color: #2d3a5a !important;
}

:deep(html.dark) .input-wrapper:focus-within {
  background: #16213e !important;
  border-color: #818cf8 !important;
  box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.15) !important;
}

:deep(html.dark) .login-input { color: #f1f5f9 !important; }
:deep(html.dark) .login-input::placeholder { color: #64748b !important; }
:deep(html.dark) .input-icon { color: #64748b !important; }
:deep(html.dark) .pwd-toggle { color: #64748b !important; }
:deep(html.dark) .pwd-toggle:hover { color: #94a3b8 !important; background: #1e293b !important; }

:deep(html.dark) .settings-btn {
  background: #16213e !important;
  border-color: #2d3a5a !important;
  color: #94a3b8 !important;
}

:deep(html.dark) .settings-btn:hover {
  background: #1e293b !important;
  border-color: #475569 !important;
}

:deep(html.dark) .captcha-inline__back {
  background: #16213e !important;
  border-color: #2d3a5a !important;
  color: #94a3b8 !important;
}

:deep(html.dark) .captcha-inline__title { color: #f1f5f9 !important; }
:deep(html.dark) .login-form-footer { color: #64748b !important; }
:deep(html.dark) .mobile-brand__name { color: #f1f5f9 !important; }
</style>
