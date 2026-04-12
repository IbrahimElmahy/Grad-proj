import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

export default function ForgotPasswordPage() {
  const [email,   setEmail]   = useState('')
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!email) { setError('Please enter your email address.'); return }
    if (!/\S+@\S+\.\S+/.test(email)) { setError('Please enter a valid email address.'); return }
    setError('')
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      navigate('/reset-password')
    }, 1000)
  }

  return (
    <div className="min-h-screen bg-white grid md:grid-cols-2">

      {/* ── LEFT — form panel ── */}
      <div className="flex flex-col">

        {/* Navbar */}
        <header className="flex items-center justify-between px-8 pt-6 pb-4">
          <Link to="/login" className="flex items-center gap-2.5">
            <svg viewBox="0 0 32 32" width="28" height="28">
              <polygon points="16,2 30,16 16,30 2,16" fill="#1a6bff"/>
              <polygon points="16,7 25,16 16,25 7,16" fill="white"/>
            </svg>
            <div>
              <p className="font-bold text-slate-900 text-[15px] leading-none">RVMS</p>
              <p className="text-slate-400 text-[10px] tracking-wider">RUNWAY VISION</p>
            </div>
          </Link>
          <span className="text-slate-500 text-sm hidden sm:block">Runway Vision Monitoring System</span>
        </header>

        {/* Form area */}
        <div className="flex-1 flex items-center justify-center px-8 py-12">
          <motion.div
            className="w-full max-w-[380px]"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.28 }}
          >
            <h2 className="text-[28px] font-bold text-slate-900 mb-2 text-center">Forgot Password</h2>
            <p className="text-slate-500 text-sm text-center mb-8">
              Enter the email associated with your account.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email field */}
              <div className="relative">
                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                  </svg>
                </span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setError('') }}
                  placeholder="Email Address"
                  className="w-full pl-10 pr-4 py-3 bg-slate-100 border border-transparent rounded-xl text-sm text-slate-800 outline-none transition-all focus:bg-white focus:border-brand-500 focus:ring-2 focus:ring-brand-500/10 placeholder:text-slate-400"
                />
              </div>

              <AnimatePresence>
                {error && (
                  <motion.p
                    className="text-red-500 text-[13px] bg-red-50 border border-red-200 px-3 py-2 rounded-lg"
                    initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                  >
                    {error}
                  </motion.p>
                )}
              </AnimatePresence>

              <motion.button
                type="submit"
                disabled={loading}
                whileTap={{ scale: 0.98 }}
                className="w-full py-3 rounded-xl bg-brand-500 text-white font-semibold text-[15px] hover:bg-brand-600 transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed shadow-lg shadow-brand-500/25"
              >
                {loading && (
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"/>
                )}
                {loading ? 'Please wait…' : 'Reset Password'}
              </motion.button>
            </form>

            <p className="text-center text-sm text-slate-500 mt-5">
              Remember your password?{' '}
              <Link to="/login" className="text-brand-500 font-semibold hover:underline">Sign in.</Link>
            </p>
          </motion.div>
        </div>

        {/* Footer */}
        <footer className="px-8 pb-6 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400">
          <span>© 2026 Runway Vision Monitoring System (RVMS). All rights reserved.</span>
          <span>Authorized Personnel Access Only. Compliance: FAA/EASA Standard CS-25.</span>
        </footer>
      </div>

      {/* ── RIGHT — photo panel ── */}
   
      
      <div className="hidden md:block relative overflow-hidden">

        {/* ── SINGLE PHOTO variant (default) ── */}
        <img
          src="/images/forgot-bg.jpg"
          alt="Aviation"
          className="absolute inset-0 w-full h-full object-cover"
          onError={(e) => { e.target.style.display = 'none' }}
        />

        {/* Fallback gradient shown while / if no photo is present */}
        <div className="absolute inset-0 bg-gradient-to-b from-slate-700 to-slate-900" style={{ zIndex: -1 }}/>

        {/* Optional dark overlay to improve contrast */}
        <div className="absolute inset-0 bg-black/20"/>

        

          <div className="flex flex-col h-full">
            <div className="flex-1 relative overflow-hidden">
              <img src="../src/imgs/Forget-pass-pic.jpg"className="absolute inset-0 w-full h-full object-cover"/>
            </div>
            
          </div>
       
      </div>

    </div>
  )
}
