import { motion } from 'framer-motion'

export default function StatCard({ label, value, sub, icon, iconBg = 'bg-brand-50', valueColor, delay = 0 }) {
  return (
    <motion.div
      className="card p-5 flex items-start gap-4"
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28, delay }}
    >
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${iconBg}`}>
        {icon}
      </div>
      <div>
        <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">{label}</p>
        <h3 className={`text-2xl font-bold leading-none ${valueColor || 'text-slate-900'}`}>{value}</h3>
        {sub && <span className="text-xs text-slate-400 mt-1 block">{sub}</span>}
      </div>
    </motion.div>
  )
}
