import instance from './index'

export function getPushSchedules() {
  return instance.get('/push-schedules')
}

export function getPushSchedule(id) {
  return instance.get(`/push-schedules/${id}`)
}

export function createPushSchedule(data) {
  return instance.post('/push-schedules', data)
}

export function updatePushSchedule(id, data) {
  return instance.put(`/push-schedules/${id}`, data)
}

export function deletePushSchedule(id) {
  return instance.delete(`/push-schedules/${id}`)
}

export function triggerPushSchedule(id) {
  return instance.post(`/push-schedules/${id}/trigger`)
}

export function getPushLogs(scheduleId) {
  const params = scheduleId ? { schedule_id: scheduleId } : {}
  return instance.get('/push-schedules/logs', { params })
}
