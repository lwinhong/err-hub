import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { login as loginApi, logout as logoutApi, getMe } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_admin === true)

  async function login(username, password, captcha_id) {
    const res = await loginApi(username, password, captcha_id)
    token.value = res.data.access_token
    refreshToken.value = res.data.refresh_token
    localStorage.setItem('token', token.value)
    localStorage.setItem('refreshToken', refreshToken.value)
    await fetchUser()
  }

  async function logout() {
    try {
      await logoutApi()
    } catch {
      // 即使后端调用失败，也清理前端状态
    }
    token.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  async function fetchUser() {
    try {
      const res = await getMe()
      user.value = res.data
    } catch {
      logout()
    }
  }

  return { token, refreshToken, user, isAuthenticated, isAdmin, login, logout, fetchUser }
})
