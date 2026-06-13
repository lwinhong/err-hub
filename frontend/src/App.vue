<template>
  <el-config-provider :locale="elementLocale">
    <el-container v-if="authStore.isAuthenticated" class="h-full overflow-hidden">
      <el-header class="app-header p-0 border-b z-10 overflow-hidden" :class="{ 'mobile-menu-open': mobileMenuOpen }"
        style="border-color: var(--el-border-color-light); background-color: var(--el-fill-color-blank); box-shadow: 0 1px 4px rgba(0,0,0,0.08)">
        <!-- 桌面端：菜单 + 控件 -->
        <div class="flex items-center h-[58px] px-5 max-md:hidden">
          <span class="flex items-center shrink-0 mr-4">
            <img src="/favicon.svg" alt="ErrHub" class="logo-icon" />
            <span class="logo-text">ErrHub</span>
          </span>
          <el-menu mode="horizontal" :default-active="activeMenu" :ellipsis="false" class="flex-1 h-[60px] !border-b-0"
            router>
            <el-menu-item index="/">
              <el-icon>
                <DataAnalysis />
              </el-icon>
              <span>{{ t('app.dashboard') }}</span>
            </el-menu-item>
            <el-menu-item index="/projects">
              <el-icon>
                <FolderOpened />
              </el-icon>
              <span>{{ t('app.projects') }}</span>
            </el-menu-item>
            <el-menu-item v-if="authStore.isAdmin" index="/admin">
              <el-badge :value="t('app.adminBadge')" :offset="[0, 12]">
                <div class="flex items-center gap-1">
                  <el-icon><Setting /></el-icon>
                  <span>{{ t('app.admin') }}</span>
                </div>
              </el-badge>
            </el-menu-item>
          </el-menu>
          <div class="flex items-center h-[60px] shrink-0 gap-2">
            <el-dropdown trigger="click" @command="handleLangChange">
              <button class="settings-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              </button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="lang in languages" :key="lang.code" :command="lang.code"
                    :class="{ 'is-active': locale === lang.code }">{{ lang.label }}</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <button class="settings-btn" @click="handleToggleDark">
              <svg v-if="isDark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
            </button>
            <el-tooltip :content="t('app.logout')" placement="bottom" :show-after="300">
              <button class="settings-btn" @click="handleLogout">
                <el-icon :size="18"><SwitchButton /></el-icon>
              </button>
            </el-tooltip>
          </div>
        </div>
        <!-- 移动端：Logo + 汉堡按钮 -->
        <div class="hidden md:hidden flex items-center justify-between h-14 px-4 max-md:flex">
          <span class="flex items-center"><img src="/favicon.svg" alt="ErrHub" class="logo-icon" /><span class="logo-text">ErrHub</span></span>
          <div class="flex items-center gap-1">
            <el-dropdown trigger="click" @command="handleLangChange">
              <button class="settings-btn settings-btn--sm">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              </button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="lang in languages" :key="lang.code" :command="lang.code"
                    :class="{ 'is-active': locale === lang.code }">{{ lang.label }}</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <button class="settings-btn settings-btn--sm" @click="handleToggleDark">
              <svg v-if="isDark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
            </button>
            <div
              class="hamburger flex items-center justify-center w-9 h-9 cursor-pointer rounded-md transition-colors hover:bg-[var(--el-fill-color-light)]"
              style="color: var(--el-text-color-regular)" @click="mobileMenuOpen = !mobileMenuOpen">
              <el-icon :size="22">
                <component :is="mobileMenuOpen ? Close : Expand" />
              </el-icon>
            </div>
          </div>
        </div>
        <!-- 移动端下拉菜单 -->
        <transition name="slide-down">
          <div v-if="mobileMenuOpen" class="mobile-menu flex flex-col border-t"
            style="border-color: var(--el-border-color-lighter); background: var(--el-bg-color-overlay)">
            <div
              class="mobile-menu-item flex items-center gap-2.5 py-3.5 px-5 cursor-pointer text-sm transition-colors hover:bg-[var(--el-fill-color-light)] hover:text-[var(--el-color-primary)]"
              style="color: var(--el-text-color-regular)" @click="navigateTo('/')">
              <el-icon>
                <DataAnalysis />
              </el-icon><span>{{ t('app.dashboard') }}</span>
            </div>
            <div
              class="mobile-menu-item flex items-center gap-2.5 py-3.5 px-5 cursor-pointer text-sm transition-colors hover:bg-[var(--el-fill-color-light)] hover:text-[var(--el-color-primary)]"
              style="color: var(--el-text-color-regular)" @click="navigateTo('/projects')">
              <el-icon>
                <FolderOpened />
              </el-icon><span>{{ t('app.projects') }}</span>
            </div>
            <div v-if="authStore.isAdmin"
              class="mobile-menu-item flex items-center gap-2.5 py-3.5 px-5 cursor-pointer text-sm transition-colors hover:bg-[var(--el-fill-color-light)] hover:text-[var(--el-color-primary)]"
              style="color: var(--el-text-color-regular)" @click="navigateTo('/admin')">
              <el-icon>
                <Setting />
              </el-icon><span>{{ t('app.admin') }}</span>
            </div>
            <div
              class="mobile-menu-item flex items-center gap-2.5 py-3.5 px-5 cursor-pointer text-sm transition-colors hover:bg-[var(--el-fill-color-light)] hover:text-[var(--el-color-primary)]"
              style="color: var(--el-text-color-regular)" @click="handleLogout">
              <el-icon>
                <SwitchButton />
              </el-icon><span>{{ t('app.logout') }}</span>
            </div>
          </div>
        </transition>
      </el-header>
      <el-main class="app-main overflow-y-auto p-0"
        style="background-color: var(--el-bg-color-page); height: calc(100vh - 60px)">
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
import {
  DataAnalysis, FolderOpened, Setting, Close, Expand, SwitchButton
} from '@element-plus/icons-vue'
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

const currentLangLabel = computed(() => {
  return languages.find(l => l.code === locale.value)?.label || locale.value
})

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
:deep(.el-main) {
  --el-main-padding: 0;
}
:deep(.el-header) {
  --el-header-padding: 0;
}

.app-header {
  height: 60px !important;

  &.mobile-menu-open {
    height: auto !important;
  }
}

.logo-icon {
  width: 32px;
  height: 32px;
  margin-right: 8px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--el-color-primary);
  letter-spacing: 1px;
  white-space: nowrap;
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
  color: var(--el-text-color-regular);
}

.settings-btn:hover {
  background: var(--el-fill-color);
  border-color: var(--el-border-color);
  color: var(--el-color-primary);
}

.settings-btn svg {
  width: 18px;
  height: 18px;
}

.settings-btn:active {
  transform: scale(0.95);
}

.settings-btn--sm {
  width: 32px;
  height: 32px;
}

.settings-btn--sm svg {
  width: 16px;
  height: 16px;
}

:deep(.el-dropdown-menu__item.is-active) {
  color: var(--el-color-primary);
  font-weight: 600;
}

.admin-badge :deep(.el-badge__content) {
  font-size: 10px;
}

.hamburger {
  display: none;
}

.mobile-menu {
  display: none;
}

/* ── 过渡动画 ── */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.25s ease;
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

/* ── 移动端适配 ── */
@media (max-width: 768px) {
  .hamburger {
    display: flex;
  }

  .mobile-menu {
    display: flex;
  }

  .app-main {
    height: calc(100vh - 56px) !important;
  }
}
</style>
