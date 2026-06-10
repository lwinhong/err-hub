import request from './index'

export function getSettings() {
  return request.get('settings')
}

export function updateSettings(data) {
  return request.put('settings', data)
}
