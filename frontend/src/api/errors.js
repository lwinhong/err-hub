import request from './index'

export function getProjectErrors(projectId, params) {
  return request.get(`/api/v1/projects/${projectId}/errors`, { params })
}

export function getError(id) {
  return request.get(`/api/v1/errors/${id}`)
}

export function updateError(id, data) {
  return request.put(`/api/v1/errors/${id}`, data)
}

export function getErrorStats(projectId) {
  return request.get(`/api/v1/projects/${projectId}/errors/stats`)
}
