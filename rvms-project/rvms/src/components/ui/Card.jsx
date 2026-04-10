import { motion } from 'framer-motion'

export default function Card({ children, className = '', animate = false, onClick, padding = 'p-5' }) {
  const base = `card ${padding} ${className} ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}`
  if (animate) {
    return (
      <motion.div
        className={base}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
        onClick={onClick}
      >
        {children}
      </motion.div>
    )
  }
  return <div className={base} onClick={onClick}>{children}</div>
}

export function CardHeader({ title, subtitle, action, className = '' }) {
  return (
    <div className={`flex items-center justify-between mb-4 ${className}`}>
      <div>
        <h3 className="text-[15px] font-semibold text-slate-800">{title}</h3>
        {subtitle && <p className="text-[12px] text-slate-500 mt-0.5">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}
