import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useAppStore } from '@/store/appStore'
import { useAlertsStore } from '@/store/alertsStore'
import { useClock } from '@/hooks/useClock'
import { 
  Bell, 
  Mail, 
  HelpCircle, 
  Search, 
  Check, 
  Send, 
  Info, 
  AlertTriangle, 
  ShieldAlert, 
  MailOpen, 
  LifeBuoy
} from 'lucide-react'

export default function Navbar({ title }) {
  const navigate = useNavigate()
  const { setSearchOpen } = useAppStore()
  const counts = useAlertsStore((s) => s.getCounts())
  const { alerts, resolveAlert, fetchAlerts } = useAlertsStore()
  const { display } = useClock()

  // Dropdown / Modal States
  const [notifOpen, setNotifOpen] = useState(false)
  const [mailOpen, setMailOpen] = useState(false)
  const [helpOpen, setHelpOpen] = useState(false)

  // Mail form states
  const [mailTo, setMailTo] = useState('safety-desk@rvms-aviation.com')
  const [mailSubject, setMailSubject] = useState(`RVMS Status Update - ${new Date().toLocaleDateString()}`)
  const [mailBody, setMailBody] = useState('Reporting current runway conditions: visibility is clear and automated scans are functioning normally.')
  const [mailSending, setMailSending] = useState(false)
  const [mailSentSuccess, setMailSentSuccess] = useState(false)

  // Ref for closing notification dropdown on click outside
  const notifRef = useRef(null)

  useEffect(() => {
    // Fetch alerts on mount
    fetchAlerts()
  }, [])

  useEffect(() => {
    function handleClickOutside(event) {
      if (notifRef.current && !notifRef.current.contains(event.target)) {
        setNotifOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSendMail = (e) => {
    e.preventDefault()
    setMailSending(true)
    setTimeout(() => {
      setMailSending(false)
      setMailSentSuccess(true)
      setTimeout(() => {
        setMailSentSuccess(false)
        setMailOpen(false)
        // Reset mail form
        setMailSubject(`RVMS Status Update - ${new Date().toLocaleDateString()}`)
        setMailBody('Reporting current runway conditions: visibility is clear and automated scans are functioning normally.')
      }, 2000)
    }, 1500)
  }

  const activeAlerts = alerts.filter(a => !a.resolved).slice(0, 5)

  return (
    <header className="h-[60px] bg-white border-b border-slate-200 flex items-center px-6 gap-4 sticky top-0 z-40 shadow-sm">
      <span className="text-[16px] font-semibold text-slate-800 mr-2">{title}</span>

      {/* Search trigger */}
      <button
        onClick={() => setSearchOpen(true)}
        className="flex-1 max-w-xs flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-400 text-[13px] hover:border-slate-300 hover:bg-white transition-all group"
      >
        <Search className="w-3.5 h-3.5 flex-shrink-0" />
        <span>Search activities, logs, or alerts…</span>
        <kbd className="ml-auto text-[10px] bg-slate-200 px-1.5 py-0.5 rounded font-mono hidden group-hover:block">⌘K</kbd>
      </button>

      <div className="ml-auto flex items-center gap-3">
        {/* Clock */}
        <span className="text-[13px] text-slate-500 font-medium tabular-nums hidden md:block">{display}</span>

        {/* Mail Button */}
        <button 
          onClick={() => setMailOpen(true)}
          className="w-9 h-9 rounded-lg flex items-center justify-center text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors relative"
          title="Compose Mail"
        >
          <Mail className="w-4 h-4" />
        </button>

        {/* Notifications Button */}
        <div className="relative" ref={notifRef}>
          <button 
            onClick={() => setNotifOpen(!notifOpen)}
            className="w-9 h-9 rounded-lg flex items-center justify-center text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors relative"
            title="Notifications"
          >
            <Bell className="w-4 h-4" />
            {counts.all > 0 && (
              <span className="absolute top-1.5 right-1.5 w-4 h-4 bg-red-500 rounded-full border border-white text-[9px] font-bold text-white flex items-center justify-center">
                {counts.all}
              </span>
            )}
          </button>

          {/* Notifications Dropdown */}
          <AnimatePresence>
            {notifOpen && (
              <motion.div 
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                className="absolute right-0 mt-2 w-80 bg-white border border-slate-200 rounded-2xl shadow-xl z-50 overflow-hidden"
              >
                <div className="px-4 py-3 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
                  <span className="font-bold text-slate-800 text-sm">Active Alerts</span>
                  <span className="text-xs bg-brand-100 text-brand-700 font-semibold px-2 py-0.5 rounded-full">{counts.all} active</span>
                </div>

                <div className="max-h-64 overflow-y-auto divide-y divide-slate-100">
                  {activeAlerts.length > 0 ? (
                    activeAlerts.map((alert) => (
                      <div key={alert.id} className="p-3 hover:bg-slate-50 transition-colors flex gap-2">
                        <div className="mt-0.5 flex-shrink-0">
                          {alert.severity === 'critical' ? (
                            <ShieldAlert className="w-4 h-4 text-red-500" />
                          ) : (
                            <AlertTriangle className="w-4 h-4 text-yellow-500" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p 
                            onClick={() => {
                              setNotifOpen(false)
                              navigate(`/alerts/${alert.id}`)
                            }}
                            className="font-semibold text-slate-800 text-xs truncate hover:underline cursor-pointer"
                          >
                            {alert.title}
                          </p>
                          <p className="text-[10px] text-slate-500 truncate mt-0.5">{alert.desc}</p>
                          <span className="text-[9px] text-slate-400 mt-1 block">{alert.time}</span>
                        </div>
                        <button
                          onClick={() => resolveAlert(alert.id)}
                          className="w-6 h-6 rounded-full hover:bg-green-50 border border-slate-200 hover:border-green-200 flex items-center justify-center text-slate-400 hover:text-green-600 transition-all self-center"
                          title="Resolve Alert"
                        >
                          <Check className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ))
                  ) : (
                    <div className="p-8 text-center text-slate-400 text-xs">
                      No active alerts. Runway is safe.
                    </div>
                  )}
                </div>

                <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-100 text-center">
                  <Link 
                    to="/history" 
                    onClick={() => setNotifOpen(false)}
                    className="text-xs text-brand-500 hover:text-brand-600 font-semibold"
                  >
                    View All Audit History
                  </Link>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Help Button */}
        <button 
          onClick={() => setHelpOpen(true)}
          className="w-9 h-9 rounded-lg flex items-center justify-center text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors"
          title="Help & Info"
        >
          <HelpCircle className="w-4 h-4" />
        </button>
      </div>

      {/* ======================================================== */}
      {/* Mail Modal */}
      {/* ======================================================== */}
      <AnimatePresence>
        {mailOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMailOpen(false)}
              className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative bg-white rounded-3xl overflow-hidden shadow-2xl border border-slate-100 max-w-lg w-full z-10"
            >
              <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
                <h3 className="font-bold text-slate-800 text-base flex items-center gap-2">
                  <MailOpen className="w-5 h-5 text-brand-500" />
                  Compose Safety Report
                </h3>
                <button 
                  onClick={() => setMailOpen(false)}
                  className="w-8 h-8 rounded-full bg-slate-50 hover:bg-slate-100 text-slate-400 hover:text-slate-600 flex items-center justify-center transition-all"
                >
                  ✕
                </button>
              </div>

              {mailSentSuccess ? (
                <div className="p-10 text-center space-y-4">
                  <div className="w-16 h-16 rounded-full bg-green-50 text-green-500 flex items-center justify-center mx-auto text-2xl shadow-sm">
                    ✓
                  </div>
                  <h4 className="font-bold text-slate-800 text-lg">Email Sent Successfully</h4>
                  <p className="text-sm text-slate-500">Your report has been successfully dispatched to the Safety Desk.</p>
                </div>
              ) : (
                <form onSubmit={handleSendMail} className="p-6 space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">To</label>
                    <input 
                      type="email" 
                      required
                      value={mailTo}
                      onChange={(e) => setMailTo(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Subject</label>
                    <input 
                      type="text" 
                      required
                      value={mailSubject}
                      onChange={(e) => setMailSubject(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-brand-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Message Body</label>
                    <textarea 
                      required
                      rows={5}
                      value={mailBody}
                      onChange={(e) => setMailBody(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-brand-500 resize-none"
                    />
                  </div>

                  <div className="flex justify-end gap-3 border-t border-slate-100 pt-4 mt-2">
                    <button 
                      type="button"
                      onClick={() => setMailOpen(false)}
                      className="px-4 py-2.5 rounded-xl text-sm font-medium text-slate-500 hover:bg-slate-100 transition-all"
                    >
                      Cancel
                    </button>
                    <button 
                      type="submit"
                      disabled={mailSending}
                      className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-brand-500 hover:bg-brand-600 text-white transition-all flex items-center gap-2 shadow-sm disabled:opacity-75"
                    >
                      {mailSending ? (
                        <>
                          <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          Sending...
                        </>
                      ) : (
                        <>
                          <Send className="w-4 h-4" />
                          Send Message
                        </>
                      )}
                    </button>
                  </div>
                </form>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ======================================================== */}
      {/* Help Modal */}
      {/* ======================================================== */}
      <AnimatePresence>
        {helpOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setHelpOpen(false)}
              className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative bg-white rounded-3xl overflow-hidden shadow-2xl border border-slate-100 max-w-xl w-full z-10"
            >
              <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
                <h3 className="font-bold text-slate-800 text-base flex items-center gap-2">
                  <LifeBuoy className="w-5 h-5 text-brand-500" />
                  RVMS Help & Documentation
                </h3>
                <button 
                  onClick={() => setHelpOpen(false)}
                  className="w-8 h-8 rounded-full bg-slate-50 hover:bg-slate-100 text-slate-400 hover:text-slate-600 flex items-center justify-center transition-all"
                >
                  ✕
                </button>
              </div>

              <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
                <div className="space-y-4">
                  <div className="flex gap-3 items-start">
                    <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Info className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="font-bold text-slate-800 text-sm">System Overview</h4>
                      <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                        The Runway Visibility Monitoring System (RVMS) uses advanced AI algorithms (including YOLO object detection and Gemini suggestions) to audit visibility camera feeds. It flags foreign object debris (FOD), low visibility sectors, and other hazards in real-time.
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-3 items-start">
                    <div className="w-8 h-8 rounded-lg bg-yellow-50 text-yellow-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <AlertTriangle className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="font-bold text-slate-800 text-sm">Alert Classification</h4>
                      <ul className="text-xs text-slate-500 mt-1 space-y-1 list-disc list-inside">
                        <li><span className="font-semibold text-red-600">Critical</span>: High risk objects or fog that compromises operations immediately.</li>
                        <li><span className="font-semibold text-yellow-600">Warning</span>: Objects or conditions requiring inspection within the hour.</li>
                        <li><span className="font-semibold text-green-600">Safe</span>: Scans with no foreign objects and good visibility.</li>
                      </ul>
                    </div>
                  </div>

                  <div className="flex gap-3 items-start">
                    <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Send className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="font-bold text-slate-800 text-sm">Manual Overhead Scan</h4>
                      <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                        Safety officers can upload an image or video manually via the main Dashboard. The upload will be sent to the backend pipeline for object detection and analysis.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="border-t border-slate-100 pt-4 text-center">
                  <p className="text-xs text-slate-400">Need direct administrator assistance?</p>
                  <p className="text-xs text-slate-600 font-semibold mt-1">Contact IT Support at support@rvms-aviation.com or Ext: 1042</p>
                </div>
              </div>

              <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end">
                <button 
                  onClick={() => setHelpOpen(false)}
                  className="px-5 py-2 rounded-xl text-sm font-semibold bg-brand-500 hover:bg-brand-600 text-white transition-all shadow-sm"
                >
                  Got It
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </header>
  )
}
