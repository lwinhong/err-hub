import axios from 'axios'
import { ElMessage } from 'element-plus'
import i18n from '../i18n'

const instance = axios.create({
  baseURL: 'api/v1',
  timeout: 15000
})

let isRefreshing = false
let pendingRequests = []

instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

instance.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    const originalRequest = error.config

    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      const refreshTokenValue = localStorage.getItem('refreshToken')

      if (!refreshTokenValue) {
        clearAuth()
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve) => {
          pendingRequests.push((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(instance(originalRequest))
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      return new Promise((resolve) => {
        axios
          .post('api/v1/auth/refresh', { refresh_token: refreshTokenValue })
          .then((res) => {
            const newToken = res.data.access_token
            localStorage.setItem('token', newToken)
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            pendingRequests.forEach((cb) => cb(newToken))
            pendingRequests = []
            resolve(instance(originalRequest))
          })
          .catch(() => {
            pendingRequests = []
            clearAuth()
            return Promise.reject(error)
          })
          .finally(() => {
            isRefreshing = false
          })
      })
    }

    return Promise.reject(error)
  }
)

function clearAuth() {
  localStorage.removeItem('token')
  localStorage.removeItem('refreshToken')
  if (window.location.hash !== '#/login') {
    ElMessage.error(i18n.global.t('api.sessionExpired'))
    window.location.hash = '#/login'
  }
}

export default instance
