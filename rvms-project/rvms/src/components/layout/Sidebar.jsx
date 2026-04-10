import { NavLink, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore } from '@/store/authStore'
import { useAlertsStore } from '@/store/alertsStore'

const NAV_ITEMS = [
  {
    to: '/dashboard',
    label: 'Dashboard',
    icon: (
      <svg className="w-[17px] h-[17px]" fill="currentColor" viewBox="0 0 24 24">
        <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
      </svg>
    ),
  },
  {
    to: '/alerts',
    label: 'Alerts',
    badge: true,
    icon: (
      <svg className="w-[17px] h-[17px]" fill="currentColor" viewBox="0 0 24 24">
        <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
      </svg>
    ),
  },
]

export default function Sidebar() {
  const { user, logout } = useAuthStore()
  const counts = useAlertsStore((s) => s.getCounts())
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside className="w-[220px] bg-slate-900 flex flex-col fixed top-0 left-0 h-screen z-50 overflow-y-auto">
      {/* Logo */}
      <div className="px-4 pt-5 pb-3 border-b border-white/[0.07] mb-2">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 bg-brand-500 rounded-xl flex items-center justify-center flex-shrink-0">
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
            </svg>
          </div>
          <div>
            <h1 className="text-white text-[15px] font-bold tracking-wide">RVMS</h1>
            <p className="text-white/40 text-[10px] leading-tight">Runway Vision Monitoring</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2.5 py-2">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            {item.icon}
            <span>{item.label}</span>
            {item.badge && counts.critical > 0 && (
              <span className="ml-auto bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full leading-none">
                {counts.critical}
              </span>
            )}
          </NavLink>
        ))}

        {/* Divider */}
        <div className="border-t border-white/[0.06] my-3" />

        {/* System status pill */}
        <div className="mx-1 px-3 py-2.5 rounded-xl bg-green-500/10 border border-green-500/20">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse flex-shrink-0" />
            <div>
              <p className="text-green-400 text-[11px] font-semibold">All Systems Nominal</p>
              <p className="text-white/30 text-[10px] mt-0.5">24/24 sensors active</p>
            </div>
          </div>
        </div>
      </nav>

      {/* User footer */}
      <div className="border-t border-white/[0.08] p-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-400 to-purple-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
            {user?.name?.split(' ').map((n) => n[0]).join('') || 'CM'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white text-[12px] font-semibold truncate">{user?.name || 'Captain Miller'}</p>
            <p className="text-white/35 text-[10px] truncate">{user?.id || 'RVMS-0422'}</p>
          </div>
          <button
            onClick={handleLogout}
            title="Logout"
            className="w-7 h-7 rounded-lg flex items-center justify-center text-white/30 hover:text-white/70 hover:bg-white/10 transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
            </svg>
          </button>
        </div>
      </div>
    </aside>
  )
}
