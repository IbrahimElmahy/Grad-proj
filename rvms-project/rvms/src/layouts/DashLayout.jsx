import { Outlet, useLocation } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import Sidebar from '@/components/layout/Sidebar'
import Navbar from '@/components/layout/Navbar'
import SearchModal from '@/components/ui/SearchModal'

const PAGE_TITLES = {
  '/dashboard': 'Safety Control Center',
  '/alerts':    'Safety Alerts',
  '/history':   'Scan History',
  '/settings':  'Settings',
}

export default function DashLayout() {
  const location = useLocation()
  const title = PAGE_TITLES[location.pathname] || 'RVMS'

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <div className="ml-[220px] flex-1 flex flex-col min-h-screen">
        <Navbar title={title} />
        <AnimatePresence mode="wait">
          <motion.main
            key={location.pathname}
            className="flex-1 p-6"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.22 }}
          >
            <Outlet />
          </motion.main>
        </AnimatePresence>
      </div>
      <SearchModal />
    </div>
  )
}
