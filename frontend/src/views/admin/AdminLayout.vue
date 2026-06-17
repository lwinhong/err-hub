<template>
  <el-container class="h-full overflow-hidden relative">
    <!-- 移动端遮罩 -->
    <transition name="fade">
      <div v-if="sidebarOpen" class="admin-overlay" @click="sidebarOpen = false"></div>
    </transition>

    <!-- 侧边栏 -->
    <aside class="admin-aside" :class="{ 'is-open': sidebarOpen }">
      <div class="sidebar-inner">
        <div class="sidebar-header">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          <span>{{ t('admin.title') }}</span>
        </div>
        <nav class="sidebar-nav">
          <router-link
            v-for="item in adminMenuItems"
            :key="item.path"
            :to="item.path"
            class="sidebar-link"
            :class="{ active: activeMenu === item.path }"
            @click="onMenuItemClick"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" v-html="item.svg"></svg>
            <span>{{ t(item.labelKey) }}</span>
          </router-link>
        </nav>
      </div>
    </aside>

    <!-- 右侧内容区 -->
    <el-main class="admin-main overflow-y-auto p-0 relative" style="background-color: var(--el-bg-color-page)">
      <!-- 移动端切换按钮 -->
      <button class="admin-mobile-toggle" @click="sidebarOpen = !sidebarOpen">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </button>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useMediaQuery } from '@vueuse/core'

const route = useRoute()
const { t } = useI18n()

const sidebarOpen = ref(false)
const isMobile = useMediaQuery('(max-width: 768px)')

const adminMenuItems = [
  {
    path: '/admin/settings',
    labelKey: 'admin.settings',
    svg: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>'
  },
  {
    path: '/admin/users',
    labelKey: 'admin.users',
    svg: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
  },
  {
    path: '/admin/push',
    labelKey: 'admin.push',
    svg: '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>'
  },
]

const activeMenu = computed(() => route.path)

const onMenuItemClick = () => {
  if (isMobile.value) sidebarOpen.value = false
}
</script>

<style scoped>
.admin-overlay {
  position: fixed;
  inset: 0;
  top: 56px;
  background: rgba(0, 0, 0, 0.4);
  z-index: 99;
  backdrop-filter: blur(2px);
}

/* ── 侧边栏 ── */
.admin-aside {
  width: 220px;
  flex-shrink: 0;
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-lighter);
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-inner {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 20px 16px;
  font-size: 15px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.sidebar-nav {
  padding: 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-regular);
  text-decoration: none;
  transition: all 0.2s;
}

.sidebar-link:hover {
  background: var(--el-fill-color-light);
  color: var(--el-color-primary);
}

.sidebar-link.active {
  background: rgba(var(--el-color-primary-rgb), 0.08);
  color: var(--el-color-primary);
  font-weight: 600;
}

/* ── 移动端切换按钮 ── */
.admin-mobile-toggle {
  display: none;
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 98;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, #6366f1, #818cf8);
  color: #fff;
  cursor: pointer;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
  transition: all 0.2s;
}

.admin-mobile-toggle:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(99, 102, 241, 0.5);
}

/* ── 过渡动画 ── */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ── 移动端适配 ── */
@media (max-width: 768px) {
  .admin-mobile-toggle {
    display: flex;
  }

  .admin-aside {
    position: fixed;
    left: 0;
    top: 52px;
    bottom: 0;
    z-index: 100;
    width: 260px;
    transform: translateX(-100%);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 2px 0 16px rgba(0, 0, 0, 0.1);
  }

  .admin-aside.is-open {
    transform: translateX(0);
  }
}
</style>
