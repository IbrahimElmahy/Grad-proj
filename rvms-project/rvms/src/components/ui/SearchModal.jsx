import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAppStore } from '@/store/appStore'
import { SEARCH_RESULTS } from '@/data/mockData'

export default function SearchModal() {
  const { searchOpen, setSearchOpen } = useAppStore()
  const inputRef = useRef(null)

  useEffect(() => {
    if (searchOpen) setTimeout(() => inputRef.current?.focus(), 50)
    const handler = (e) => { if (e.key === 'Escape') setSearchOpen(false) }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [searchOpen, setSearchOpen])

  return (
    <AnimatePresence>
      {searchOpen && (
        <motion.div
          className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-start justify-center pt-24 px-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => setSearchOpen(false)}
        >
          <motion.div
            className="bg-white rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden"
            initial={{ opacity: 0, y: -20, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.97 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-3 px-5 py-4 border-b border-slate-100">
              <svg className="w-4 h-4 text-slate-400 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                <path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
              </svg>
              <input
                ref={inputRef}
                type="text"
                placeholder="Search activities, logs, or alerts…"
                className="flex-1 text-[15px] text-slate-800 outline-none placeholder:text-slate-400"
              />
              <kbd className="text-[11px] text-slate-400 bg-slate-100 px-2 py-0.5 rounded font-mono">ESC</kbd>
            </div>
            <div className="py-2">
              <p className="px-5 py-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Recent</p>
              {SEARCH_RESULTS.map((r, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 px-5 py-2.5 hover:bg-slate-50 cursor-pointer"
                  onClick={() => setSearchOpen(false)}
                >
                  <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-sm flex-shrink-0">
                    {r.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-slate-700 truncate">{r.label}</p>
                  </div>
                  <span className="text-[11px] text-slate-400 bg-slate-100 px-2 py-0.5 rounded font-medium">{r.type}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
