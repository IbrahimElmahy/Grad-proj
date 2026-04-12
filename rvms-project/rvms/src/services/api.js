import axios from 'axios'
import { RECENT_SCANS, ALERTS_DATA, HISTORY_SCANS } from '@/data/mockData'

// Create a mock axios instance that intercepts calls and returns mock data
const api = axios.create({ baseURL: '/api', timeout: 800 })

// Response interceptor — simulate network latency & mock responses
api.interceptors.request.use((config) => {
  config._startTime = Date.now()
  return config
})

const MOCK_DB = {
  '/scans/recent': RECENT_SCANS,
  '/alerts': ALERTS_DATA,
  '/history': HISTORY_SCANS,
  '/system/status': { runwayStatus: 'Safe', systemHealth: 'Optimal', sensorsActive: 24, lastScan: '14:25:31' },
  '/auth/login': { token: 'mock-jwt-token-rvms-2024', user: { name: 'Captain Miller', role: 'Safety Officer' } },
}

api.interceptors.response.use(
  null,
  (error) => {
    // If no real network, serve mock data
    const url = error.config?.url
    if (MOCK_DB[url]) {
      return Promise.resolve({ data: MOCK_DB[url], status: 200, config: error.config })
    }
    return Promise.reject(error)
  }
)

// ── Service methods ────────────────────────────────────────────────────────

export const authService = {
  login: (email, password) =>
    new Promise((resolve) => {
      setTimeout(() => resolve({ data: { ...MOCK_DB['/auth/login'], email } }), 900)
    }),
}

export const scanService = {
  getRecent: () =>
    new Promise((resolve) => {
      setTimeout(() => resolve({ data: RECENT_SCANS }), 300)
    }),
  initiateScan: () =>
    new Promise((resolve) => {
      setTimeout(
        () =>
          resolve({
            data: {
              scanId: `#SCN-${Math.floor(8922 + Math.random() * 100)}`,
              status: 'completed',
              confidence: `${(98 + Math.random() * 1.9).toFixed(1)}%`,
              duration: `${(1.0 + Math.random() * 0.6).toFixed(1)}s`,
              fod: 'None',
            },
          }),
        2500
      )
    }),
}

export const alertsService = {
  getAll: () =>
    new Promise((resolve) => {
      setTimeout(() => resolve({ data: ALERTS_DATA }), 300)
    }),
}

export const historyService = {
  getScans: (filters = {}) =>
    new Promise((resolve) => {
      setTimeout(() => {
        let data = [...HISTORY_SCANS]
        if (filters.status && filters.status !== 'all') {
          data = data.filter((s) => s.status === filters.status)
        }
        if (filters.dateFrom) {
          data = data.filter((s) => s.dateISO >= filters.dateFrom)
        }
        if (filters.dateTo) {
          data = data.filter((s) => s.dateISO <= filters.dateTo)
        }
        resolve({ data })
      }, 300)
    }),
}

export default api
