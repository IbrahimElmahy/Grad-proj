import { create } from 'zustand'
import { ALERTS_DATA } from '@/data/mockData'

export const useAlertsStore = create((set, get) => ({
  alerts: ALERTS_DATA,
  filter: 'all',
  setFilter: (f) => set({ filter: f }),
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
