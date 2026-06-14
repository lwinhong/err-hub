import request from './index'

export function getUsers(params) {
  return request.get('users', { params })
}

export function createUser(data) {
  return request.post('users', data)
}

export function updateUser(userId, data) {
  return request.put(`users/${userId}`, data)
}

export function resetUserPassword(userId, password) {
  return request.put(`users/${userId}/reset-password`, { password })
}

export function deleteUser(userId) {
  return request.delete(`users/${userId}`)
}

export function unlockUser(userId) {
  return request.post(`users/${userId}/unlock`)
}
