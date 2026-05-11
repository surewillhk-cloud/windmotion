import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    const settings = localStorage.getItem('windmotion-settings')
    if (settings) {
      const parsed = JSON.parse(settings)
      if (parsed.apiKey) {
        config.headers.Authorization = `Bearer ${parsed.apiKey}`
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        console.error('Unauthorized: Invalid API key')
      } else if (status === 429) {
        console.error('Rate limited. Retry after:', error.response.headers['retry-after'])
      } else if (status >= 500) {
        console.error('Server error:', data?.message || 'Unknown error')
      }
    } else if (error.request) {
      console.error('Network error: No response received')
    }
    return Promise.reject(error)
  }
)

// Whale endpoints
export const whaleApi = {
  list: () => api.get('/whales'),
  get: (id: string) => api.get(`/whales/${id}`),
  create: (data: any) => api.post('/whales', data),
  update: (id: string, data: any) => api.put(`/whales/${id}`, data),
  delete: (id: string) => api.delete(`/whales/${id}`),
  feed: (params?: any) => api.get('/whales/feed', { params }),
  analyze: (id: string) => api.post(`/whales/${id}/analyze`)
}

// Analysis endpoints
export const analysisApi = {
  list: () => api.get('/analysis'),
  get: (id: string) => api.get(`/analysis/${id}`),
  create: (data: any) => api.post('/analysis', data),
  forward: (whaleId: string) => api.post(`/analysis/forward/${whaleId}`),
  reverse: (whaleId: string) => api.post(`/analysis/reverse/${whaleId}`),
  status: (id: string) => api.get(`/analysis/${id}/status`),
  graph: (id: string) => api.get(`/analysis/${id}/graph`),
  report: (id: string) => api.get(`/analysis/${id}/report`),
  replay: (id: string) => api.get(`/analysis/${id}/replay`)
}

// Filter endpoints
export const filterApi = {
  list: () => api.get('/filters'),
  get: (id: string) => api.get(`/filters/${id}`),
  create: (data: any) => api.post('/filters', data),
  update: (id: string, data: any) => api.put(`/filters/${id}`, data),
  delete: (id: string) => api.delete(`/filters/${id}`),
  run: (id: string) => api.post(`/filters/${id}/run`),
  results: (id: string, params?: any) => api.get(`/filters/${id}/results`, { params })
}

// Recommend endpoints
export const recommendApi = {
  whales: () => api.get('/recommend/whales'),
  tokens: () => api.get('/recommend/tokens'),
  strategies: () => api.get('/recommend/strategies')
}

// System endpoints
export const systemApi = {
  status: () => api.get('/system/status'),
  quota: () => api.get('/system/quota')
}

export default api
