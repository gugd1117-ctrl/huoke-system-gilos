import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1', timeout: 120000 })

export const listSearchModes = () => api.get('/meta/search-modes').then(r => r.data)
export const listPlatforms = () => api.get('/meta/platforms').then(r => r.data)
export const expandKeywords = (query, mode) => api.post('/keywords/expand', null, { params: { query, search_mode: mode } }).then(r => r.data)

export const createTask = (query, search_mode, platforms) =>
  api.post('/tasks', { query, search_mode, platforms }).then(r => r.data)
export const listTasks = (limit = 50) => api.get('/tasks', { params: { limit } }).then(r => r.data)
export const getTask = (id) => api.get(`/tasks/${id}`).then(r => r.data)
export const startTask = (id) => api.post(`/tasks/${id}/start`).then(r => r.data)

export const listLeads = (taskId, params) => api.get(`/tasks/${taskId}/leads`, { params }).then(r => r.data)
export const reportMdUrl = (taskId) => `/api/v1/tasks/${taskId}/report.md`
export const reportHtmlUrl = (taskId) => `/api/v1/tasks/${taskId}/report.html`
export const exportXlsxUrl = (taskId, high = true) =>
  `/api/v1/tasks/${taskId}/export.xlsx?high_intent_only=${high ? 'true' : 'false'}`
