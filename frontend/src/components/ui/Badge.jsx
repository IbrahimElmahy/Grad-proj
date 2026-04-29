const MAP = {
  critical:  'badge-critical',
  warning:   'badge-warning',
  safe:      'badge-safe',
  completed: 'badge-completed',
  flagged:   'badge-flagged',
  pending:   'badge-pending',
  info:      'badge-info',
}

const DOTS = {
  critical: 'bg-red-500',
  warning:  'bg-amber-500',
  safe:     'bg-green-500',
  completed:'bg-blue-500',
  flagged:  'bg-red-500',
}

export default function Badge({ variant = 'info', dot = false, children, className = '' }) {
  return (
    <span className={`badge ${MAP[variant] || MAP.info} ${className}`}>
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${DOTS[variant] || 'bg-slate-400'}`} />}
      {children || variant}
    </span>
  )
}
