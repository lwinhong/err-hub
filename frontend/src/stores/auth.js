import { defineStore } from 'pinia'
import { login as loginApi, getMe } from '../api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    refreshToken: localStorage.getItem('refreshToken') || '',
    user: null
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.is_admin === true
  },
  actions: {
    async login(username, password) {
      const res = await loginApi(username, password)
      this.token = res.data.access_token
      this.refreshToken = res.data.refresh_token
      localStorage.setItem('token', this.token)
      localStorage.setItem('refreshToken', this.refreshToken)
      await this.fetchUser()
    },
    logout() {
      this.token = ''
      this.refreshToken = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
    },
    async fetchUser() {
      try {
        const res = await getMe()
        this.user = res.data
      } catch {
        this.logout()
      }
    }
  }
})
