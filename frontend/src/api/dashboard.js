import request from './index'

export function getOverview(params) {
  return request.get('dashboard/overview', { params })
}

export function getDistributions(params) {
  return request.get('dashboard/distributions', { params })
}

export function getProjectTrend(projectId, days) {
  return request.get(`dashboard/projects/${projectId}/trend`, { params: { days } })
}
