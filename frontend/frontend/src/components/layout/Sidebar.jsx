import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useAlertsStore } from '@/store/alertsStore'

const NAV_ITEMS = [
  {
    to: '/dashboard',
    label: 'Dashboard',
    icon: (
      <svg
        className="w-[17px] h-[17px]"
        fill="currentColor"
        viewBox="0 0 24 24"
      >
        <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" />
      </svg>
    ),
  },

  {
    to: '/alerts',
    label: 'Alerts',
    badge: true,
    icon: (
      <svg
        className="w-[17px] h-[17px]"
        fill="currentColor"
        viewBox="0 0 24 24"
      >
        <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z" />
      </svg>
    ),
  },

  {
    to: '/history',
    label: 'History',
    icon: (
      <svg
        className="w-[17px] h-[17px]"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  },

  {
    to: '/settings',
    label: 'Settings',
    icon: (
      <svg
        className="w-[17px] h-[17px]"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
        />

        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
        />
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
            <svg
              className="w-5 h-5 text-white"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z" />
            </svg>
          </div>

          <div>
            <h1 className="text-white text-[15px] font-bold tracking-wide">
              RVMS
            </h1>

            <p className="text-white/40 text-[10px] leading-tight">
              Runway Vision Monitoring
            </p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2.5 py-2">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `nav-item ${isActive ? 'active' : ''}`
            }
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

        <div className="border-t border-white/[0.06] my-3" />

        <div className="mx-1 px-3 py-2.5 rounded-xl bg-green-500/10 border border-green-500/20">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse flex-shrink-0" />

            <div>
              <p className="text-green-400 text-[11px] font-semibold">
                All Systems Nominal
              </p>

              <p className="text-white/30 text-[10px] mt-0.5">
                24/24 sensors active
              </p>
            </div>
          </div>
        </div>
      </nav>

      {/* Footer */}
      <div className="border-t border-white/[0.08] p-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-400 to-purple-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
            {user?.name
              ?.split(' ')
              .map((n) => n[0])
              .join('') || 'CM'}
          </div>

          <div className="flex-1 min-w-0">
            <p className="text-white text-[12px] font-semibold truncate">
              {user?.name || 'Captain Miller'}
            </p>

            <p className="text-white/35 text-[10px] truncate">
              {user?.id || 'RVMS-0422'}
            </p>
          </div>

          <button
            onClick={handleLogout}
            title="Logout"
            className="w-7 h-7 rounded-lg flex items-center justify-center text-white/30 hover:text-white/70 hover:bg-white/10 transition-colors"
          >
            <svg
              className="w-3.5 h-3.5"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z" />
            </svg>
          </button>
        </div>
      </div>
    </aside>
  )
}