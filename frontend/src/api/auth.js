import request from './index'

export function login(username, password) {
  return request.post('/api/v1/auth/login', { username, password })
}

export function refreshToken(refresh_token) {
  return request.post('/api/v1/auth/refresh', { refresh_token })
}

export function getMe() {
  return request.get('/api/v1/auth/me')
}

export function changePassword(old_password, new_password) {
  return request.put('/api/v1/auth/me/password', { old_password, new_password })
}
