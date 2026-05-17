import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set) => ({
      isLoggedIn: false,
      user: null,
      token: null,
      login: ({ user, token }) => {
        set({
          isLoggedIn: true,
          user,
          token,
        })
      },
      logout: () => set({ isLoggedIn: false, user: null, token: null }),
    }),
    { name: 'rvms-auth' }
  )
)
