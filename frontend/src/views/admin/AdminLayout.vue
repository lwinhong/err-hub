<template>
  <el-container class="admin-container">
    <!-- 移动端遮罩 -->
    <transition name="fade">
      <div v-if="sidebarOpen" class="admin-overlay" @click="sidebarOpen = false"></div>
    </transition>

    <!-- 侧边栏 -->
    <el-aside :width="sidebarWidth" class="admin-aside" :class="{ 'is-open': sidebarOpen }">
      <div class="admin-sidebar">
        <div class="sidebar-title">{{ t('admin.title') }}</div>
        <el-menu :default-active="activeMenu" router class="sidebar-menu">
          <el-menu-item
            v-for="item in adminMenuItems"
            :key="item.path"
            :index="item.path"
            @click="onMenuItemClick"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <template #title>{{ t(item.labelKey) }}</template>
          </el-menu-item>
        </el-menu>
      </div>
    </el-aside>

    <!-- 右侧内容区 -->
    <el-main class="admin-main">
      <!-- 移动端切换按钮 -->
      <div class="admin-mobile-toggle" @click="sidebarOpen = !sidebarOpen">
        <el-icon :size="18"><Menu /></el-icon>
      </div>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { User, Menu } from '@element-plus/icons-vue'

const route = useRoute()
const { t } = useI18n()

const sidebarOpen = ref(false)
const isMobile = ref(false)

// 侧边栏菜单配置 —— 新增管理页面只需在此追加
const adminMenuItems = [
  { path: '/admin/users', icon: User, labelKey: 'admin.users' },
]

const activeMenu = computed(() => route.path)

const sidebarWidth = computed(() => isMobile.value ? '260px' : '220px')

const onMenuItemClick = () => {
  if (isMobile.value) {
    sidebarOpen.value = false
  }
}

// 响应式断点监听
let mql = null
onMounted(() => {
  mql = window.matchMedia('(max-width: 768px)')
  isMobile.value = mql.matches
  const handler = (e) => { isMobile.value = e.matches }
  mql.addEventListener('change', handler)
  onBeforeUnmount(() => mql.removeEventListener('change', handler))
})
</script>

<style scoped lang="scss">
/* ── 容器 ── */
.admin-container {
  height: 100%;
  overflow: hidden;
  position: relative;
}

/* ── 遮罩 ── */
.admin-overlay {
  display: none;
  position: fixed;
  inset: 0;
  top: 60px;
  background: rgba(0, 0, 0, 0.35);
  z-index: 99;
}

/* ── 侧边栏 ── */
.admin-aside {
  border-right: 1px solid var(--el-border-color-light);
  background-color: var(--el-fill-color-blank);
  overflow-y: auto;
  overflow-x: hidden;
  transition: transform 0.3s ease;
}

.admin-sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar-title {
  padding: 18px 20px 14px;
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  flex-shrink: 0;
}

.sidebar-menu {
  border-right: none !important;
  flex: 1;
}

/* ── 右侧内容区 ── */
.admin-main {
  overflow-y: auto;
  padding: 0;
  background-color: var(--el-bg-color-page);
  position: relative;
}

/* ── 移动端切换按钮 ── */
.admin-mobile-toggle {
  display: none;
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 98;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background-color: var(--el-color-primary);
  color: #fff;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s;

  &:hover {
    transform: scale(1.05);
  }
}

/* ── 遮罩淡入淡出 ── */
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
  .admin-overlay {
    display: block;
  }

  .admin-aside {
    position: fixed;
    left: 0;
    top: 56px;
    bottom: 0;
    z-index: 100;
    width: 260px !important;
    transform: translateX(-100%);
    box-shadow: 2px 0 12px rgba(0, 0, 0, 0.15);

    &.is-open {
      transform: translateX(0);
    }
  }

  .admin-mobile-toggle {
    display: flex;
  }
}
</style>
