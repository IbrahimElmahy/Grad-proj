import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { authService } from '@/services/api'

function scorePassword(pwd) {
  if (!pwd) return { label: '', color: '', segments: [false, false, false, false] }
  let score = 0
  if (pwd.length >= 8)          score++
  if (pwd.length >= 12)         score++
  if (/[A-Z]/.test(pwd))        score++
  if (/[0-9]/.test(pwd))        score++
  if (/[^A-Za-z0-9]/.test(pwd)) score++
  if (score <= 1) return { label: 'WEAK',        color: '#ef4444', segments: [true,  false, false, false] }
  if (score === 2) return { label: 'FAIR',        color: '#f97316', segments: [true,  true,  false, false] }
  if (score === 3) return { label: 'GOOD',        color: '#eab308', segments: [true,  true,  true,  false] }
  if (score === 4) return { label: 'STRONG',      color: '#22c55e', segments: [true,  true,  true,  true]  }
  return               { label: 'VERY STRONG',    color: '#16a34a', segments: [true,  true,  true,  true]  }
}

export default function ResetPasswordPage() {
  const [pwd,      setPwd]      = useState('')
  const [confirm,  setConfirm]  = useState('')
  const [showPwd,  setShowPwd]  = useState(false)
  const [showConf, setShowConf] = useState(false)
  const [loading,  setLoading]  = useState(false)
  const [done,     setDone]     = useState(false)
  const [error,    setError]    = useState('')
  const navigate = useNavigate()
  const location = useLocation()
  const query = new URLSearchParams(location.search)
  const resetToken = query.get('token') || location.state?.token || ''
  const resetEmail = query.get('email') || location.state?.email || ''

  const strength = scorePassword(pwd)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!resetToken)     { setError('Reset token is missing. Please restart the password reset flow.'); return }
    if (!pwd)            { setError('Please enter a new password.');              return }
    if (pwd.length < 12) { setError('Password must be at least 12 characters.'); return }
    if (pwd !== confirm) { setError('Passwords do not match.');                   return }
    setError('')
    setLoading(true)
    try {
      await authService.resetPassword({
        token: resetToken,
        password: pwd,
        password_confirm: confirm,
      })
      setLoading(false)
      setDone(true)
      setTimeout(() => navigate('/login'), 2200)
    } catch (apiError) {
      setLoading(false)
      setError(apiError?.response?.data?.detail || 'Could not reset password.')
    }
  }

  const EyeIcon = ({ visible }) => (
    <svg className="w-[18px] h-[18px]" fill="currentColor" viewBox="0 0 24 24">
      {visible
        ? <path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zm10 12.73c-2.76 0-5-2.24-5-5 0-.77.18-1.5.49-2.14l1.57 1.57c-.03.18-.06.37-.06.57 0 1.66 1.34 3 3 3 .2 0 .38-.03.57-.07l1.57 1.57c-.65.32-1.37.5-2.14.5zm2.97-5.33c-.15-1.4-1.25-2.5-2.64-2.64l2.64 2.64z"/>
        : <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
      }
    </svg>
  )

  return (
    <div className="min-h-screen flex flex-col" style={{ background: '#f0f2f5' }}>

      {/* ── Navbar ── */}
      <header className="bg-white h-14 flex items-center justify-between px-8 border-b border-slate-200">
        <Link to="/login" className="flex items-center gap-2">
          <svg viewBox="0 0 32 32" width="26" height="26">
            <polygon points="16,2 30,16 16,30 2,16" fill="#1a6bff"/>
            <polygon points="16,7 25,16 16,25 7,16" fill="white"/>
          </svg>
          <span className="font-bold text-slate-900 text-[15px]">RVMS</span>
        </Link>
        <span className="text-slate-500 text-sm hidden sm:block">Runway Vision Monitoring System</span>
      </header>

      {/* ── Content ── */}
      <main className="flex-1 flex flex-col items-center justify-start px-4 pt-8 pb-10">
        <AnimatePresence mode="wait">
          {done ? (
            <motion.div
              key="success"
              className="text-center mt-20"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Password Updated!</h2>
              <p className="text-slate-400 text-sm">Redirecting you to login…</p>
            </motion.div>
          ) : (
            <motion.div
              key="form"
              className="w-full max-w-[560px]"
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.27 }}
            >
              {/* ── Hero illustration ── */}
              <div
                className="rounded-2xl overflow-hidden"
                style={{ borderBottomLeftRadius: 0, borderBottomRightRadius: 0 }}
              >
                <div
                  className="h-[160px] flex items-center justify-center relative"
                  style={{ background: 'linear-gradient(145deg,#eef2ff 0%,#f0f5ff 55%,#e8edff 100%)' }}
                >
                  {/* Concentric rings */}
                  <div className="absolute w-[108px] h-[108px] rounded-full border-[14px] border-[#dde8ff]" />
                  <div className="absolute w-[76px]  h-[76px]  rounded-full border-[8px]  border-[#c5d5f8]" />

                  {/* Lock button */}
                  <div className="relative z-10 w-[62px] h-[62px] rounded-full bg-white shadow flex items-center justify-center border border-[#d0deff]">
                    <svg className="w-[28px] h-[28px] text-[#9ab2e8]" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
                      <rect x="5" y="11" width="14" height="10" rx="2.5" strokeLinejoin="round"/>
                      <path d="M8 11V7a4 4 0 0 1 8 0v4" strokeLinecap="round"/>
                      <circle cx="12" cy="16" r="1.4" fill="currentColor" stroke="none"/>
                    </svg>
                    {/* Refresh badge */}
                    <div className="absolute -top-1.5 -right-1.5 w-6 h-6 rounded-full bg-brand-400 border-2 border-white flex items-center justify-center">
                      <svg className="w-[11px] h-[11px] text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
                      </svg>
                    </div>
                  </div>
                </div>
              </div>

              {/* ── Heading ── */}
              <div className="text-center py-5">
                <h1 className="text-[26px] font-bold text-slate-900 mb-2">Reset Password</h1>
                <p className="text-slate-500 text-[13.5px] leading-relaxed max-w-xs mx-auto">
                  Choose a strong, unique password to secure your aviation monitoring account.
                </p>
                {resetEmail && (
                  <p className="text-[12px] text-brand-600 mt-2">Resetting password for {resetEmail}</p>
                )}
              </div>

              {/* ── Form card ── */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm px-7 py-6">
                <form onSubmit={handleSubmit} className="space-y-5">

                  {/* New Password */}
                  <div>
                    <label className="block text-[13px] font-medium text-slate-700 mb-1.5">
                      New Password
                    </label>
                    <div className="relative">
                      <input
                        type={showPwd ? 'text' : 'password'}
                        value={pwd}
                        onChange={(e) => { setPwd(e.target.value); setError('') }}
                        placeholder="Enter new password"
                        className="w-full px-4 py-[11px] pr-11 border border-slate-200 rounded-xl text-[13.5px] text-slate-800 bg-white outline-none transition-all placeholder:text-slate-400 focus:border-brand-400 focus:ring-2 focus:ring-brand-400/10"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPwd(!showPwd)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                      >
                        <EyeIcon visible={showPwd} />
                      </button>
                    </div>

                    {/* 4-segment strength bar */}
                    <AnimatePresence>
                      {pwd.length > 0 && (
                        <motion.div
                          className="mt-2"
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                        >
                          <div className="flex gap-1 mb-1">
                            {strength.segments.map((filled, i) => (
                              <div
                                key={i}
                                className="h-[3px] flex-1 rounded-full transition-colors duration-300"
                                style={{ background: filled ? strength.color : '#e2e8f0' }}
                              />
                            ))}
                          </div>
                          <p
                            className="text-[10px] font-bold tracking-[0.08em]"
                            style={{ color: strength.color }}
                          >
                            PASSWORD STRENGTH: {strength.label}
                          </p>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>

                  {/* Confirm Password */}
                  <div>
                    <label className="block text-[13px] font-medium text-slate-700 mb-1.5">
                      Confirm Password
                    </label>
                    <div className="relative">
                      <input
                        type={showConf ? 'text' : 'password'}
                        value={confirm}
                        onChange={(e) => { setConfirm(e.target.value); setError('') }}
                        placeholder="Repeat new password"
                        className={`w-full px-4 py-[11px] pr-11 border rounded-xl text-[13.5px] text-slate-800 bg-white outline-none transition-all placeholder:text-slate-400 focus:ring-2 ${
                          confirm && pwd !== confirm
                            ? 'border-red-400 focus:border-red-400 focus:ring-red-400/10'
                            : confirm && pwd === confirm
                            ? 'border-green-400 focus:border-green-400 focus:ring-green-400/10'
                            : 'border-slate-200 focus:border-brand-400 focus:ring-brand-400/10'
                        }`}
                      />
                      <button
                        type="button"
                        onClick={() => setShowConf(!showConf)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                      >
                        <EyeIcon visible={showConf} />
                      </button>
                    </div>
                  </div>

                  {/* Error */}
                  <AnimatePresence>
                    {error && (
                      <motion.p
                        className="text-red-500 text-[12.5px] bg-red-50 border border-red-200 px-3 py-2 rounded-lg"
                        initial={{ opacity: 0, y: -4 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                      >
                        {error}
                      </motion.p>
                    )}
                  </AnimatePresence>

                  {/* Submit button */}
                  <motion.button
                    type="submit"
                    disabled={loading}
                    whileTap={{ scale: 0.98 }}
                    className="w-full py-3 rounded-xl bg-brand-500 hover:bg-brand-600 text-white font-semibold text-[14.5px] transition-all flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed shadow-md shadow-brand-500/20"
                  >
                    {loading && (
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    )}
                    {loading ? 'Updating…' : 'Reset Password →'}
                  </motion.button>
                </form>

                {/* Security standards */}
                <div className="mt-5 flex gap-3 rounded-xl px-4 py-3.5 border border-blue-100 bg-blue-50/60">
                  <div className="mt-0.5 w-[18px] h-[18px] rounded-full border border-brand-300 bg-brand-50 flex items-center justify-center flex-shrink-0">
                    <svg className="w-[10px] h-[10px] text-brand-500" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
                    </svg>
                  </div>
                  <div>
                    <p className="text-[12px] font-semibold text-slate-700 mb-1">Security Standards</p>
                    <p className="text-[11.5px] text-slate-500 leading-relaxed">
                      Passwords must be at least 12 characters and include a mix of uppercase, numbers, and special symbols for compliance with aviation safety protocols.
                    </p>
                  </div>
                </div>
              </div>

              {/* Bottom links */}
              <div className="flex items-center justify-between mt-4 px-1">
                <Link
                  to="/login"
                  className="flex items-center gap-1 text-[13px] text-slate-500 hover:text-slate-800 transition-colors"
                >
                  <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6z"/>
                  </svg>
                  Back to Login
                </Link>
                <button className="text-[13px] text-slate-500 hover:text-slate-800 transition-colors">
                  Need help?
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* ── Footer ── */}
      <footer className="py-4 text-center space-y-0.5">
        <p className="text-[11.5px] text-slate-400">
          © 2026 Runway Vision Monitoring System (RVMS). All rights reserved.
        </p>
        <p className="text-[11px] text-slate-400">
          Authorized Personnel Access Only. Compliance: FAA/EASA Standard CS-25.
        </p>
      </footer>
    </div>
  )
}
