<template>
  <el-config-provider :locale="elementLocale">
    <el-container v-if="authStore.isAuthenticated" class="h-full overflow-hidden">
      <el-header class="app-header" :class="{ 'mobile-menu-open': mobileMenuOpen }">
        <!-- 桌面端 -->
        <div class="header-inner">
          <div class="header-brand" @click="router.push('/')">
            <img src="/favicon.svg" alt="ErrHub" class="logo-icon" />
            <span class="logo-text">ErrHub</span>
          </div>
          <nav class="header-nav">
            <router-link to="/" class="nav-item" :class="{ active: activeMenu === '/' }">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
              <span>{{ t('app.dashboard') }}</span>
            </router-link>
            <router-link to="/projects" class="nav-item" :class="{ active: activeMenu === '/projects' }">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
              <span>{{ t('app.projects') }}</span>
            </router-link>
            <router-link v-if="authStore.isAdmin" to="/admin" class="nav-item" :class="{ active: activeMenu === '/admin' }">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
              <span>{{ t('app.admin') }}</span>
            </router-link>
          </nav>
          <div class="header-actions">
            <el-dropdown trigger="click" @command="handleLangChange">
              <button class="action-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              </button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="lang in languages" :key="lang.code" :command="lang.code" :class="{ 'is-active': locale === lang.code }">{{ lang.label }}</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <button class="action-btn" @click="handleToggleDark">
              <svg v-if="isDark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
            </button>
            <el-tooltip :content="t('app.logout')" placement="bottom" :show-after="300">
              <button class="action-btn" @click="handleLogout">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
              </button>
            </el-tooltip>
          </div>
        </div>
        <!-- 移动端 -->
        <div class="header-mobile">
          <div class="header-brand" @click="router.push('/')">
            <img src="/favicon.svg" alt="ErrHub" class="logo-icon" />
            <span class="logo-text">ErrHub</span>
          </div>
          <div class="header-actions">
            <button class="action-btn" @click="handleToggleDark">
              <svg v-if="isDark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
            </button>
            <button class="hamburger" @click="mobileMenuOpen = !mobileMenuOpen">
              <svg v-if="!mobileMenuOpen" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
        </div>
        <!-- 移动端菜单 -->
        <transition name="slide-down">
          <div v-if="mobileMenuOpen" class="mobile-menu">
            <div class="mobile-menu-item" @click="navigateTo('/')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
              <span>{{ t('app.dashboard') }}</span>
            </div>
            <div class="mobile-menu-item" @click="navigateTo('/projects')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
              <span>{{ t('app.projects') }}</span>
            </div>
            <div v-if="authStore.isAdmin" class="mobile-menu-item" @click="navigateTo('/admin')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
              <span>{{ t('app.admin') }}</span>
            </div>
            <div class="mobile-menu-divider"></div>
            <div class="mobile-menu-item" @click="handleLogout">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
              <span>{{ t('app.logout') }}</span>
            </div>
          </div>
        </transition>
      </el-header>
      <el-main class="app-main overflow-y-auto p-0" style="background-color: var(--el-bg-color-page); height: calc(100vh - 60px)">
        <router-view />
      </el-main>
    </el-container>
    <router-view v-else />
  </el-config-provider>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDark, useToggle } from '@vueuse/core'
import { useI18n } from 'vue-i18n'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'
import { useAuthStore } from './stores/auth'
import { useSettingsStore } from './stores/settings'
import { STORAGE_KEY, languages } from './i18n'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const settingsStore = useSettingsStore()
const isDark = useDark()
const toggleDark = useToggle(isDark)
const mobileMenuOpen = ref(false)
const { t, locale } = useI18n()

const elementLocale = computed(() => locale.value === 'zh-CN' ? zhCn : en)

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

watch(locale, () => {
  document.title = `${t('login.title')} - ${t('login.subtitle')}`
}, { immediate: true })

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUser()
  }
  if (authStore.isAuthenticated) {
    settingsStore.fetchSettings()
  }
})

const activeMenu = computed(() => {
  if (route.path.startsWith('/projects')) return '/projects'
  if (route.path.startsWith('/admin')) return '/admin'
  return route.path
})

const handleLogout = () => {
  mobileMenuOpen.value = false
  authStore.logout()
  router.push('/login')
}

const navigateTo = (path) => {
  mobileMenuOpen.value = false
  router.push(path)
}
</script>

<style>
@import './styles/main.css';
</style>

<style scoped lang="scss">
:deep(.el-main) { --el-main-padding: 0; }
:deep(.el-header) { --el-header-padding: 0; height: auto !important; }

.app-header {
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  position: relative;
  z-index: 100;

  &.mobile-menu-open {
    .header-mobile { border-bottom-color: var(--el-border-color-lighter); }
  }
}

.header-inner {
  display: flex;
  align-items: center;
  height: 56px;
  padding: 0 20px;
  gap: 8px;

  @media (max-width: 768px) {
    display: none;
  }
}

.header-mobile {
  display: none;
  align-items: center;
  justify-content: space-between;
  height: 52px;
  padding: 0 16px;

  @media (max-width: 768px) {
    display: flex;
  }
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  flex-shrink: 0;
  padding-right: 16px;
}

.logo-icon {
  width: 30px;
  height: 30px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #6366f1;
  letter-spacing: -0.3px;
}

/* ── 导航项 ── */
.header-nav {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;

  @media (max-width: 768px) {
    display: none;
  }
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-regular);
  text-decoration: none;
  transition: all 0.2s;

  &:hover {
    background: var(--el-fill-color-light);
    color: var(--el-color-primary);
  }

  &.active {
    background: rgba(var(--el-color-primary-rgb), 0.08);
    color: var(--el-color-primary);
    font-weight: 600;
  }
}

/* ── 操作按钮 ── */
.header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 1px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-blank);
  border-radius: 8px;
  cursor: pointer;
  padding: 0;
  transition: all 0.2s;
  color: var(--el-text-color-secondary);

  &:hover {
    background: var(--el-fill-color-light);
    border-color: var(--el-border-color);
    color: var(--el-color-primary);
  }

  &:active {
    transform: scale(0.95);
  }
}

.hamburger {
  display: none;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 1px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-blank);
  border-radius: 8px;
  cursor: pointer;
  color: var(--el-text-color-secondary);
  transition: all 0.2s;

  @media (max-width: 768px) {
    display: flex;
  }

  &:hover {
    background: var(--el-fill-color-light);
    color: var(--el-color-primary);
  }
}

/* ── 移动端菜单 ── */
.mobile-menu {
  display: none;
  flex-direction: column;
  padding: 8px 12px 12px;
  border-top: 1px solid var(--el-border-color-lighter);

  @media (max-width: 768px) {
    display: flex;
  }
}

.mobile-menu-divider {
  height: 1px;
  background: var(--el-border-color-lighter);
  margin: 6px 0;
}

.mobile-menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 14px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-regular);
  cursor: pointer;
  transition: all 0.15s;

  &:hover {
    background: var(--el-fill-color-light);
    color: var(--el-color-primary);
  }
}

/* ── 下拉菜单 ── */
:deep(.el-dropdown-menu__item.is-active) {
  color: var(--el-color-primary);
  font-weight: 600;
}

/* ── 过渡动画 ── */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  max-height: 0;
}

.slide-down-enter-to,
.slide-down-leave-from {
  opacity: 1;
  max-height: 300px;
}
</style>
