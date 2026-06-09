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
            <el-menu-item v-if="authStore.isAdmin" index="/users">
              <el-icon>
                <User />
              </el-icon>
              <span>{{ t('app.users') }}</span>
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
                <component :is="isDark ? 'Sunny' : 'Moon'" />
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
                <component :is="isDark ? 'Sunny' : 'Moon'" />
              </el-icon>
            </div>
            <div class="hamburger" @click="mobileMenuOpen = !mobileMenuOpen">
              <el-icon :size="22">
                <component :is="mobileMenuOpen ? 'Close' : 'Expand'" />
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
            <div v-if="authStore.isAdmin" class="mobile-menu-item" @click="navigateTo('/users')">
              <el-icon>
                <User />
              </el-icon><span>{{ t('app.users') }}</span>
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

<style src="./styles/global.css"></style>
