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
              <el-icon>
                <Setting />
              </el-icon>
              <span>{{ t('app.admin') }}</span>
            </el-menu-item>
          </el-menu>
          <div class="flex items-center h-[60px] shrink-0">
            <el-dropdown @command="handleLangChange">
              <span
                class="flex items-center gap-1 cursor-pointer text-sm px-2.5 h-[60px] hover:text-[var(--el-color-primary)]"
                style="color: var(--el-text-color-regular)">
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
            <div
              class="flex items-center gap-1.5 px-5 h-[60px] cursor-pointer transition-colors hover:text-[var(--el-color-primary)]"
              style="color: var(--el-text-color-regular)" @click="handleToggleDark()">
              <el-icon>
                <component :is="isDark ? Sunny : Moon" />
              </el-icon>
              <span>{{ isDark ? t('app.light') : t('app.dark') }}</span>
            </div>
            <div
              class="flex items-center gap-1.5 px-5 h-[60px] cursor-pointer transition-colors text-sm hover:text-[var(--el-color-primary)]"
              style="color: var(--el-text-color-regular)" @click="handleLogout">
              <el-icon>
                <SwitchButton />
              </el-icon>
              <span>{{ t('app.logout') }}</span>
            </div>
          </div>
        </div>
        <!-- 移动端：Logo + 汉堡按钮 -->
        <div class="hidden md:hidden flex items-center justify-between h-14 px-4 max-md:flex">
          <span class="flex items-center"><img src="/favicon.svg" alt="ErrHub" class="logo-icon" /><span class="logo-text">ErrHub</span></span>
          <div class="flex items-center gap-1">
            <el-dropdown @command="handleLangChange">
              <span class="text-xs cursor-pointer px-2 h-9 flex items-center"
                style="color: var(--el-text-color-regular)">
                {{ currentLangLabel }}
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="lang in languages" :key="lang.code" :command="lang.code">{{ lang.label
                  }}</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <div
              class="flex items-center gap-1.5 px-2 h-9 cursor-pointer transition-colors hover:text-[var(--el-color-primary)]"
              style="color: var(--el-text-color-regular)" @click="handleToggleDark()">
              <el-icon>
                <component :is="isDark ? Sunny : Moon" />
              </el-icon>
            </div>
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

<style>
@import './styles/main.css';
</style>

<style scoped lang="scss">
:deep(.el-main) {
  --el-main-padding: 0;
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
