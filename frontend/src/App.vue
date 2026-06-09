<template>
  <el-config-provider :locale="elementLocale">
    <el-container v-if="authStore.isAuthenticated" class="app-container">
      <el-header class="app-header" :class="{ 'mobile-menu-open': mobileMenuOpen }">
        <!-- 桌面端：菜单 + 控件 -->
        <div class="desktop-header">
          <el-menu mode="horizontal" :default-active="activeMenu" :ellipsis="false" class="desktop-menu" router>
            <el-menu-item index="logo" disabled class="logo-item">
              <span class="logo-text">ErrHub</span>
            </el-menu-item>
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
              <el-icon>
                <Setting />
              </el-icon>
              <span>{{ t('app.admin') }}</span>
            </el-menu-item>
          </el-menu>
          <div class="header-actions">
            <el-dropdown @command="handleLangChange">
              <span class="lang-switch-trigger">
                <el-icon>
                  <CollectionTag />
                </el-icon>
                <span>{{ currentLangLabel }}</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="lang in languages" :key="lang.code" :command="lang.code">{{ lang.label
                  }}</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <div class="theme-toggle" @click="handleToggleDark()">
              <el-icon>
                <component :is="isDark ? Sunny : Moon" />
              </el-icon>
              <span>{{ isDark ? t('app.light') : t('app.dark') }}</span>
            </div>
            <div class="header-action-btn" @click="handleLogout">
              <el-icon>
                <SwitchButton />
              </el-icon>
              <span>{{ t('app.logout') }}</span>
            </div>
          </div>
        </div>
        <!-- 移动端：Logo + 汉堡按钮 -->
        <div class="mobile-header">
          <span class="logo-text">ErrHub</span>
          <div class="mobile-header-right">
            <el-dropdown @command="handleLangChange">
              <span class="lang-switch-trigger-mobile">
                {{ currentLangLabel }}
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="lang in languages" :key="lang.code" :command="lang.code">{{ lang.label
                  }}</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <div class="theme-toggle" @click="handleToggleDark()">
              <el-icon>
                <component :is="isDark ? Sunny : Moon" />
              </el-icon>
            </div>
            <div class="hamburger" @click="mobileMenuOpen = !mobileMenuOpen">
              <el-icon :size="22">
                <component :is="mobileMenuOpen ? Close : Expand" />
              </el-icon>
            </div>
          </div>
        </div>
        <!-- 移动端下拉菜单 -->
        <transition name="slide-down">
          <div v-if="mobileMenuOpen" class="mobile-menu">
            <div class="mobile-menu-item" @click="navigateTo('/')">
              <el-icon>
                <DataAnalysis />
              </el-icon><span>{{ t('app.dashboard') }}</span>
            </div>
            <div class="mobile-menu-item" @click="navigateTo('/projects')">
              <el-icon>
                <FolderOpened />
              </el-icon><span>{{ t('app.projects') }}</span>
            </div>
            <div v-if="authStore.isAdmin" class="mobile-menu-item" @click="navigateTo('/admin')">
              <el-icon>
                <Setting />
              </el-icon><span>{{ t('app.admin') }}</span>
            </div>
            <div class="mobile-menu-item" @click="handleLogout">
              <el-icon>
                <SwitchButton />
              </el-icon><span>{{ t('app.logout') }}</span>
            </div>
          </div>
        </transition>
      </el-header>
      <el-main class="app-main">
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
  DataAnalysis, FolderOpened, Setting, CollectionTag,
  Sunny, Moon, SwitchButton, Close, Expand
} from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'
import { useAuthStore } from './stores/auth'
import { STORAGE_KEY, languages } from './i18n'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
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

onMounted(() => {
  if (authStore.isAuthenticated && !authStore.user) {
    authStore.fetchUser()
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

<style scoped lang="scss">
/* ── 应用容器 ── */
.app-container {
  height: 100%;
  overflow: hidden;
}

/* ── 页面头部 ── */
.app-header {
  padding: 0;
  border-bottom: 1px solid var(--el-border-color-light);
  background-color: var(--el-fill-color-blank);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  z-index: 10;
  height: 60px !important;
  overflow: hidden;

  &.mobile-menu-open {
    height: auto !important;
  }
}

/* ── 桌面端 ── */
.desktop-header {
  display: flex;
  align-items: center;
  height: 58px;
  padding: 0 20px;
}

.desktop-menu {
  flex: 1;
  height: 60px;
  border-bottom: none !important;
}

.logo-item {
  pointer-events: none;

  &.el-menu-item.is-disabled {
    opacity: 1;
    color: inherit;
  }
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--el-color-primary);
  letter-spacing: 1px;
}

.header-actions {
  display: flex;
  align-items: center;
  height: 60px;
  flex-shrink: 0;
}

.lang-switch-trigger {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--el-text-color-regular);
  cursor: pointer;
  font-size: 14px;
  padding: 0 10px;
  height: 60px;

  &:hover {
    color: var(--el-color-primary);
  }
}

.lang-switch-trigger-mobile {
  font-size: 13px;
  color: var(--el-text-color-regular);
  cursor: pointer;
  padding: 0 8px;
  height: 36px;
  display: flex;
  align-items: center;
}

.theme-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 20px;
  height: 60px;
  cursor: pointer;
  color: var(--el-text-color-regular);
  transition: color 0.2s;

  &:hover {
    color: var(--el-color-primary);
  }
}

.header-action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 20px;
  height: 60px;
  cursor: pointer;
  color: var(--el-text-color-regular);
  transition: color 0.2s;
  font-size: 14px;

  &:hover {
    color: var(--el-color-primary);
  }
}

/* ── 移动端头部 ── */
.mobile-header {
  display: none;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 16px;
}

.mobile-header-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.hamburger {
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  cursor: pointer;
  border-radius: 6px;
  color: var(--el-text-color-regular);
  transition: background-color 0.2s;

  &:hover {
    background-color: var(--el-fill-color-light);
  }
}

/* ── 移动端下拉菜单 ── */
.mobile-menu {
  display: none;
  flex-direction: column;
  border-top: 1px solid var(--el-border-color-lighter);
  background: var(--el-bg-color-overlay);
}

.mobile-menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  cursor: pointer;
  color: var(--el-text-color-regular);
  transition: background-color 0.2s, color 0.2s;
  font-size: 14px;

  &:hover {
    background-color: var(--el-fill-color-light);
    color: var(--el-color-primary);
  }
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

/* ── 主内容区 ── */
.app-main {
  background-color: var(--el-bg-color-page);
  height: calc(100vh - 60px);
  overflow-y: auto;
  padding: 0;
}

/* ── 移动端适配 ── */
@media (max-width: 768px) {
  .desktop-header {
    display: none !important;
  }

  .mobile-header {
    display: flex;
  }

  .hamburger {
    display: flex;
  }

  .mobile-menu {
    display: flex;
  }

  .mobile-header .theme-toggle {
    height: 36px;
    padding: 0 8px;
  }

  .app-main {
    height: calc(100vh - 56px);
  }
}
</style>
