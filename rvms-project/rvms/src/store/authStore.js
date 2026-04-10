import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set) => ({
      isLoggedIn: false,
      user: null,
      login: (credentials) => {
        // Mock auth — accept any credentials
        set({
          isLoggedIn: true,
          user: {
            name: 'Captain Miller',
            email: credentials?.email || 'c.miller@rvms.aero',
            id: 'RVMS-0422',
            role: 'Safety Officer',
            airport: 'Heathrow — EGLL',
          },
        })
      },
      logout: () => set({ isLoggedIn: false, user: null }),
    }),
    { name: 'rvms-auth' }
  )
)
