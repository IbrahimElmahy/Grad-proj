import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'

import LoginPage from '@/pages/LoginPage'
import ForgotPasswordPage from '@/pages/ForgotPasswordPage'
import ResetPasswordPage from '@/pages/ResetPasswordPage'

import DashLayout from '@/layouts/DashLayout'

import DashboardPage from '@/pages/DashboardPage'
import AlertsPage from '@/pages/AlertsPage'
import History from '@/pages/History'
import Settings from '@/pages/Settings'
import AlertDetails from '@/pages/AlertDetails'

function ProtectedRoute({ children }) {
  const isLoggedIn = useAuthStore((s) => s.isLoggedIn)

  return isLoggedIn ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/forgot-password"
        element={<ForgotPasswordPage />}
      />

      <Route
        path="/reset-password"
        element={<ResetPasswordPage />}
      />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashLayout />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={<Navigate to="/dashboard" replace />}
        />

        <Route
          path="dashboard"
          element={<DashboardPage />}
        />

        <Route
          path="alerts"
          element={<AlertsPage />}
        />

        <Route
          path="history"
          element={<History />}
        />

        <Route
          path="settings"
          element={<Settings />}
        />

        <Route
          path="alerts/:id"
          element={<AlertDetails />}
        />
      </Route>

      <Route
        path="*"
        element={<Navigate to="/dashboard" replace />}
      />
    </Routes>
  )
}