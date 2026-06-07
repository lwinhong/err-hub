<template>
  <el-container v-if="authStore.isAuthenticated" class="app-container">
    <el-header class="app-header" :class="{ 'mobile-menu-open': mobileMenuOpen }">
      <!-- 桌面端：单行菜单 -->
      <el-menu
        mode="horizontal"
        :default-active="activeMenu"
        :ellipsis="false"
        class="desktop-menu"
        router
      >
        <el-menu-item index="logo" disabled class="logo-item">
          <span class="logo-text">ErrHub</span>
        </el-menu-item>
        <el-menu-item index="/">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><FolderOpened /></el-icon>
          <span>项目列表</span>
        </el-menu-item>
        <el-menu-item v-if="authStore.isAdmin" index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <div class="menu-spacer" />
        <div class="theme-toggle" @click="handleToggleDark()">
          <el-icon><component :is="isDark ? 'Sunny' : 'Moon'" /></el-icon>
          <span>{{ isDark ? '亮色' : '暗色' }}</span>
        </div>
        <el-menu-item index="logout" @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          <span>退出登录</span>
        </el-menu-item>
      </el-menu>
      <!-- 移动端：Logo + 汉堡按钮 -->
      <div class="mobile-header">
        <span class="logo-text">ErrHub</span>
        <div class="mobile-header-right">
          <div class="theme-toggle" @click="handleToggleDark()">
            <el-icon><component :is="isDark ? 'Sunny' : 'Moon'" /></el-icon>
          </div>
          <div class="hamburger" @click="mobileMenuOpen = !mobileMenuOpen">
            <el-icon :size="22"><component :is="mobileMenuOpen ? 'Close' : 'Expand'" /></el-icon>
          </div>
        </div>
      </div>
      <!-- 移动端下拉菜单 -->
      <transition name="slide-down">
        <div v-if="mobileMenuOpen" class="mobile-menu">
          <div class="mobile-menu-item" @click="navigateTo('/')">
            <el-icon><DataAnalysis /></el-icon><span>仪表盘</span>
          </div>
          <div class="mobile-menu-item" @click="navigateTo('/projects')">
            <el-icon><FolderOpened /></el-icon><span>项目列表</span>
          </div>
          <div v-if="authStore.isAdmin" class="mobile-menu-item" @click="navigateTo('/users')">
            <el-icon><User /></el-icon><span>用户管理</span>
          </div>
          <div class="mobile-menu-item" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon><span>退出登录</span>
          </div>
        </div>
      </transition>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
  <router-view v-else />
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDark, useToggle } from '@vueuse/core'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isDark = useDark()
const toggleDark = useToggle(isDark)
const mobileMenuOpen = ref(false)

const handleToggleDark = () => {
  const root = document.documentElement
  root.classList.add('theme-transition')
  toggleDark()
  setTimeout(() => {
    root.classList.remove('theme-transition')
  }, 350)
}

onMounted(() => {
  if (authStore.isAuthenticated && !authStore.user) {
    authStore.fetchUser()
  }
})

const activeMenu = computed(() => {
  if (route.path.startsWith('/projects')) return '/projects'
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
html {
  transition: background-color 0.3s ease, color 0.3s ease;
}

html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

html.dark {
  background-color: var(--el-bg-color-page);
}

.el-card {
  border-radius: 8px;
}

html.theme-transition,
html.theme-transition *,
html.theme-transition *::before,
html.theme-transition *::after {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, fill 0.3s ease !important;
}

.app-container {
  height: 100%;
  overflow: hidden;
}

.app-header {
  padding: 0;
  border-bottom: 1px solid var(--el-border-color-light);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  z-index: 10;
  height: 60px !important;
}

.app-header.mobile-menu-open {
  height: auto !important;
}

/* ── 桌面端菜单 ── */
.desktop-menu {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.logo-item {
  pointer-events: none;
}

.logo-item.el-menu-item.is-disabled {
  opacity: 1;
  color: inherit;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--el-color-primary);
  letter-spacing: 1px;
}

.menu-spacer {
  flex: 1;
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
}

.theme-toggle:hover {
  color: var(--el-color-primary);
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
}

.hamburger:hover {
  background-color: var(--el-fill-color-light);
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
}

.mobile-menu-item:hover {
  background-color: var(--el-fill-color-light);
  color: var(--el-color-primary);
}

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
  .desktop-menu {
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
