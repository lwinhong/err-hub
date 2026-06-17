import instance from './index'

export function getPushTemplates() {
  return instance.get('/push-templates')
}

export function getPushTemplate(id) {
  return instance.get(`/push-templates/${id}`)
}

export function createPushTemplate(data) {
  return instance.post('/push-templates', data)
}

export function updatePushTemplate(id, data) {
  return instance.put(`/push-templates/${id}`, data)
}

export function deletePushTemplate(id) {
  return instance.delete(`/push-templates/${id}`)
}

export function previewPushTemplate(id) {
  return instance.post(`/push-templates/${id}/preview`)
}
