import { create } from 'zustand'
import { alertsService } from '@/services/api'

export const useAlertsStore = create((set, get) => ({
  alerts: [],
  filter: 'all',
  loading: false,
  error: '',
  lastUpdated: null,
  liveConnected: false,
  socket: null,
  setFilter: (f) => set({ filter: f }),
  fetchAlerts: async () => {
    set({ loading: true, error: '' })
    try {
      const { data } = await alertsService.getAll()
      set({ alerts: data, loading: false, lastUpdated: new Date().toISOString() })
    } catch (err) {
      set({
        loading: false,
        error: err?.response?.data?.detail || err?.message || 'Failed to load alerts.',
      })
    }
  },
  connectLive: () => {
    const currentSocket = get().socket
    if (currentSocket && currentSocket.readyState <= 1) return currentSocket

    const socket = alertsService.connectLive({
      onOpen: () => set({ liveConnected: true }),
      onClose: () => set({ liveConnected: false, socket: null }),
      onError: () => set({ liveConnected: false }),
      onAlert: (incomingAlert) =>
        set((state) => {
          const deduped = state.alerts.filter((alert) => alert.id !== incomingAlert.id)
          return {
            alerts: [incomingAlert, ...deduped],
            lastUpdated: new Date().toISOString(),
          }
        }),
    })

    set({ socket })
    return socket
  },
  disconnectLive: () => {
    const socket = get().socket
    if (socket) {
      socket.close()
    }
    set({ socket: null, liveConnected: false })
  },
  resolveAlert: (id) =>
    set((s) => ({
      alerts: s.alerts.map((a) => (a.id === id ? { ...a, resolved: true } : a)),
    })),
  getFiltered: () => {
    const { alerts, filter } = get()
    const active = alerts.filter((a) => !a.resolved)
    if (filter === 'all') return active
    return active.filter((a) => a.severity === filter)
  },
  getCounts: () => {
    const active = get().alerts.filter((a) => !a.resolved)
    return {
      all: active.length,
      critical: active.filter((a) => a.severity === 'critical').length,
      warning: active.filter((a) => a.severity === 'warning').length,
      safe: active.filter((a) => a.severity === 'safe').length,
    }
  },
}))
