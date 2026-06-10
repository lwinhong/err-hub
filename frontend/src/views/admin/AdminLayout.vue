<template>
  <el-container class="h-full overflow-hidden relative">
    <!-- 移动端遮罩 -->
    <transition name="fade">
      <div v-if="sidebarOpen" class="admin-overlay fixed inset-0 top-[60px] z-[99] max-md:block hidden" style="background: rgba(0,0,0,0.35)" @click="sidebarOpen = false"></div>
    </transition>

    <!-- 侧边栏 -->
    <el-aside :width="sidebarWidth" class="admin-aside border-r overflow-y-auto overflow-x-hidden transition-transform duration-300" style="border-color: var(--el-border-color-light); background-color: var(--el-fill-color-blank)" :class="{ 'is-open': sidebarOpen }">
      <div class="h-full flex flex-col">
        <div class="pt-4.5 px-5 pb-3.5 text-xs font-semibold uppercase tracking-wide border-b shrink-0" style="color: var(--el-text-color-secondary); border-color: var(--el-border-color-lighter)">{{ t('admin.title') }}</div>
        <el-menu :default-active="activeMenu" router class="flex-1 !border-r-0">
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
    <el-main class="overflow-y-auto p-0 relative" style="background-color: var(--el-bg-color-page)">
      <!-- 移动端切换按钮 -->
      <div class="admin-mobile-toggle hidden fixed bottom-5 right-5 z-[98] w-11 h-11 rounded-full items-center justify-center cursor-pointer transition-transform hover:scale-105 max-md:flex" style="background-color: var(--el-color-primary); color: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.2)" @click="sidebarOpen = !sidebarOpen">
        <el-icon :size="18"><Menu /></el-icon>
      </div>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useMediaQuery } from '@vueuse/core'
import { User, Menu, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const { t } = useI18n()

const sidebarOpen = ref(false)
const isMobile = useMediaQuery('(max-width: 768px)')

// 侧边栏菜单配置 —— 新增管理页面只需在此追加
const adminMenuItems = [
  { path: '/admin/users', icon: User, labelKey: 'admin.users' },
  { path: '/admin/settings', icon: Setting, labelKey: 'admin.settings' },
]

const activeMenu = computed(() => route.path)

const sidebarWidth = computed(() => isMobile.value ? '260px' : '220px')

const onMenuItemClick = () => {
  if (isMobile.value) {
    sidebarOpen.value = false
  }
}
</script>

<style scoped lang="scss">
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
}
</style>
