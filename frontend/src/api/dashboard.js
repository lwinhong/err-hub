import request from './index'

export function getOverview() {
  return request.get('dashboard/overview')
}

export function getProjectTrend(projectId, days) {
  return request.get(`dashboard/projects/${projectId}/trend`, { params: { days } })
}
