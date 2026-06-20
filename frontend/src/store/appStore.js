import { create } from 'zustand'

export const useAppStore = create((set, get) => ({
  // Theme
  darkMode: false,
  toggleDarkMode: () => {
    const next = !get().darkMode
    set({ darkMode: next })
    document.documentElement.classList.toggle('dark', next)
  },

  // Language
  language: 'English (US)',
  setLanguage: (lang) => {
    set({ language: lang })
    if (lang === 'Arabic') {
      document.documentElement.dir = 'rtl'
      document.documentElement.lang = 'ar'
    } else {
      document.documentElement.dir = 'ltr'
      document.documentElement.lang = 'en'
    }
  },

  // Active scan
  scanning: false,
  scanProgress: 0,
  startScan: () => {
    set({ scanning: true, scanProgress: 0 })
    const interval = setInterval(() => {
      const p = get().scanProgress
      if (p >= 100) {
        clearInterval(interval)
        set({ scanning: false, scanProgress: 0 })
      } else {
        set({ scanProgress: p + 5 })
      }
    }, 120)
  },

  // Search modal
  searchOpen: false,
  setSearchOpen: (v) => set({ searchOpen: v }),

  // Notifications
  notifCount: 3,
  clearNotifs: () => set({ notifCount: 0 }),
}))
