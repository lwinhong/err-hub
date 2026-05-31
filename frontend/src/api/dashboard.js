import request from './index'

export function getOverview() {
  return request.get('/api/v1/dashboard/overview')
}

export function getProjectTrend(projectId, days) {
  return request.get(`/api/v1/dashboard/projects/${projectId}/trend`, { params: { days } })
}
