import instance from './index'

export function getPushProviders() {
  return instance.get('/push-providers')
}

export function getPushProvider(id) {
  return instance.get(`/push-providers/${id}`)
}

export function createPushProvider(data) {
  return instance.post('/push-providers', data)
}

export function updatePushProvider(id, data) {
  return instance.put(`/push-providers/${id}`, data)
}

export function deletePushProvider(id) {
  return instance.delete(`/push-providers/${id}`)
}

export function testPushProvider(id) {
  return instance.post(`/push-providers/${id}/test`)
}
