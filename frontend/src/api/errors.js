import request from './index'

export function getProjectErrors(projectId, params) {
  return request.get(`projects/${projectId}/errors`, { params })
}

export function getError(id) {
  return request.get(`errors/${id}`)
}

export function updateError(id, data) {
  return request.put(`errors/${id}`, data)
}

export function deleteError(id) {
  return request.delete(`errors/${id}`)
}

export function batchDeleteErrors(ids) {
  return request.delete('errors/batch', { data: { ids } })
}

export function getErrorStats(projectId) {
  return request.get(`projects/${projectId}/errors/stats`)
}
