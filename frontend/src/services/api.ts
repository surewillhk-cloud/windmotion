import axios, { type AxiosResponse } from 'axios'

// Dynamic base URL - empty string = same domain (nginx proxy)
const API_BASE = import.meta.env.VITE_API_BASE || ''
const WS_BASE = import.meta.env.VITE_WS_BASE ||
  (location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + location.host

export { API_BASE, WS_BASE }

const api = axios.create({
  baseURL: API_BASE + '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// Inject API key from settings
api.interceptors.request.use((config) => {
  try {
    const settings = localStorage.getItem('windmotion-settings')
    if (settings) {
      const { apiKey } = JSON.parse(settings)
      if (apiKey) config.headers.Authorization = `Bearer ${apiKey}`
    }
  } catch { /* ignore */ }
  return config
}, (error) => Promise.reject(error))

// Response interceptor - unwrap data and handle errors
api.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) console.error('Unauthorized: Invalid API key')
      else if (status === 429) console.error('Rate limited. Retry after:', error.response.headers['retry-after'])
      else if (status >= 500) console.error('Server error:', data?.message || 'Unknown error')
    } else if (error.request) {
      console.error('Network error: No response received')
    }
    return Promise.reject(error)
  }
)

// ── Whale endpoints ──
export async function getWhaleFeed(chain = 'bsc', minValue = 100000, limit = 50) {
  return api.get('/whales/feed', { params: { chain, min_value: minValue, limit } })
}

export async function getWhaleDetail(address: string) {
  return api.get(`/whales/${address}`)
}

export async function startReverseAnalysis(address: string, mode = 'deep') {
  return api.post(`/whales/${address}/reverse`, { mode })
}

export async function startForwardInference(address: string) {
  return api.post(`/whales/${address}/forward`)
}

// ── Filter endpoints ──
export async function getFilters() {
  return api.get('/filters')
}

export async function createFilter(config: object) {
  return api.post('/filters', config)
}

export async function updateFilter(id: string, config: object) {
  return api.put(`/filters/${id}`, config)
}

export async function deleteFilter(id: string) {
  return api.delete(`/filters/${id}`)
}

export async function runFilter(id: string) {
  return api.post(`/filters/${id}/run`)
}

// ── Analysis endpoints ──
export async function getAnalysis(id: string) {
  return api.get(`/analysis/${id}`)
}

export async function getAnalysisProgress(id: string) {
  return api.get(`/analysis/${id}/progress`)
}

export async function getAnalysisReport(id: string) {
  return api.get(`/analysis/${id}/report`)
}

export async function getAnalysisReplay(id: string) {
  return api.get(`/analysis/${id}/replay`)
}

export async function cancelAnalysis(id: string) {
  return api.post(`/analysis/${id}/cancel`)
}

// ── History ──
export async function getHistory(page = 1, limit = 20) {
  return api.get('/history', { params: { page, limit } })
}

// ── Whale Library ──
export async function getWhaleLibrary() {
  return api.get('/library')
}

export async function addToLibrary(address: string, nickname?: string) {
  return api.post('/library', { address, nickname })
}

// ── Recommendations ──
export async function getRecommendations() {
  return api.get('/recommendations')
}

// ── Settings ──
export async function getSettings() {
  return api.get('/settings')
}

export async function updateSettings(settings: object) {
  return api.put('/settings', settings)
}

// ── Embed ──
export async function getEmbedCases() {
  return api.get('/embed/cases')
}

export async function getEmbedCase(caseId: string) {
  return api.get(`/embed/cases/${caseId}`)
}

// ── System ──
export async function getSystemStatus() {
  return api.get('/system/status')
}

export async function getSystemQuota() {
  return api.get('/system/quota')
}

export default api
