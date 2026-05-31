import request from './index'

export function getProjects(params) {
  return request.get('/api/v1/projects', { params })
}

export function createProject(data) {
  return request.post('/api/v1/projects', data)
}

export function getProject(id) {
  return request.get(`/api/v1/projects/${id}`)
}

export function updateProject(id, data) {
  return request.put(`/api/v1/projects/${id}`, data)
}

export function deleteProject(id) {
  return request.delete(`/api/v1/projects/${id}`)
}

export function regenerateToken(id) {
  return request.post(`/api/v1/projects/${id}/regenerate-token`)
}
