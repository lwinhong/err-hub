<template>
  <el-container v-if="authStore.isAuthenticated" class="app-container">
    <el-header class="app-header">
      <el-menu
        mode="horizontal"
        :default-active="activeMenu"
        :ellipsis="false"
        class="app-menu"
        router
      >
        <el-menu-item index="logo" disabled class="logo-item">
          <span class="logo-text">ErrHub</span>
        </el-menu-item>
        <el-menu-item index="/">
          <el-icon><DataAnalysis /></el-icon>
          <span>Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><FolderOpened /></el-icon>
          <span>Projects</span>
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
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
  <router-view v-else />
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDark, useToggle } from '@vueuse/core'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isDark = useDark()
const toggleDark = useToggle(isDark)

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
  authStore.logout()
  router.push('/login')
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
}

.app-header {
  padding: 0;
  border-bottom: 1px solid var(--el-border-color-light);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  z-index: 10;
}

.app-menu {
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

.app-main {
  background-color: var(--el-bg-color-page);
  min-height: calc(100vh - 60px);
}
</style>
