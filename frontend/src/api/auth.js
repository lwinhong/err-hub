import request from './index'

export function login(username, password) {
  return request.post('auth/login', { username, password })
}

export function refreshToken(refresh_token) {
  return request.post('auth/refresh', { refresh_token })
}

export function getMe() {
  return request.get('auth/me')
}

export function changePassword(old_password, new_password) {
  return request.put('auth/me/password', { old_password, new_password })
}
