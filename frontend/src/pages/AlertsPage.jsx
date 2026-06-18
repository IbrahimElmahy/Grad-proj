import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { useAlertsStore } from '@/store/alertsStore'
import Badge from '@/components/ui/Badge'
import { ALERT_TREND_24H } from '@/data/mockData'
import { formatDateTime } from '@/services/api'

const FILTER_STYLES = {
  all:      'bg-slate-800 text-white border-slate-800',
  critical: 'bg-red-50 text-red-700 border-red-300',
  warning:  'bg-amber-50 text-amber-700 border-amber-300',
  safe:     'bg-green-50 text-green-700 border-green-300',
}

function LiveCamFeed() {
  return (
    <div>
      <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">Live Vision Feed</p>
      <div className="rounded-xl overflow-hidden bg-slate-900 relative" style={{ aspectRatio: '16/10' }}>
        <svg viewBox="0 0 320 200" className="w-full h-full" preserveAspectRatio="xMidYMid slice">
          <defs>
            <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#0a1628"/>
              <stop offset="100%" stopColor="#1a2744"/>
            </linearGradient>
          </defs>
          <rect width="320" height="200" fill="url(#skyGrad)"/>
          <rect x="0" y="130" width="320" height="70" fill="#111"/>
          {/* runway */}
          <rect x="130" y="80" width="60" height="120" fill="#1a1a2e"/>
          <rect x="158" y="80" width="4"   height="120" fill="#f5d97a" opacity="0.4"/>
          {[0,1,2,3,4,5].map(i => (
            <rect key={i} x="150" y={85 + i*18} width="20" height="9" fill="#f5d97a" opacity="0.5" rx="1"/>
          ))}
          {[0,1,2,3].map(i => (
            <circle key={'l'+i} cx="133" cy={88 + i*28} r="2" fill="#f5d97a" opacity="0.8"/>
          ))}
          {[0,1,2,3].map(i => (
            <circle key={'r'+i} cx="187" cy={88 + i*28} r="2" fill="#f5d97a" opacity="0.8"/>
          ))}
          {/* scan overlay */}
          <rect x="135" y="88" width="50" height="36" fill="none" stroke="#22c55e" strokeWidth="1" strokeDasharray="3 2" opacity="0.6" rx="2"/>
          {/* HUD info */}
          <rect x="4" y="4" width="84" height="14" rx="2" fill="rgba(0,0,0,.6)"/>
          <text x="8" y="13" fill="#fff" fontSize="8" fontFamily="monospace">R-09R CAM 04</text>
          <text x="230" y="13" fill="#fff" fontSize="7" fontFamily="monospace" opacity="0.6">14:25:31 UTC</text>
          <circle cx="6" cy="24" r="3.5" fill="#ef4444"/>
          <text x="13" y="27" fill="#ef4444" fontSize="7" fontFamily="monospace">REC</text>
        </svg>
        <div className="absolute top-2 right-2 bg-black/50 text-white text-[9px] font-bold px-2 py-0.5 rounded tracking-widest">
          LIVE
        </div>
      </div>
    </div>
  )
}

export default function AlertsPage() {
  const navigate = useNavigate()
  const [confirmingAlert, setConfirmingAlert] = useState(null)

  const {
    filter,
    setFilter,
    getFiltered,
    getCounts,
    resolveAlert,
    fetchAlerts,
    connectLive,
    disconnectLive,
    loading,
    error,
    lastUpdated,
    liveConnected,
  } = useAlertsStore()

  useEffect(() => {
    fetchAlerts()
    connectLive()
    return () => disconnectLive()
  }, [fetchAlerts, connectLive, disconnectLive])

  const counts  = getCounts()
  const alerts  = getFiltered()

  const exportCSV = () => {
    const csv = [
      ["Title", "Description", "Location", "Timestamp", "Severity", "Status"],
      ...alerts.map((item) => [
        item.title,
        item.desc,
        item.location,
        item.timestamp,
        item.severity?.toUpperCase(),
        item.inspectionStatus || "Active",
      ]),
    ]
      .map((e) => e.map(val => `"${String(val).replace(/"/g, '""')}"`).join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `alerts-report-${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
  };

  const FILTERS = [
    { key: 'all',      label: `All Severities (${counts.all})` },
    { key: 'critical', label: `Critical (${counts.critical})` },
    { key: 'warning',  label: `Warning (${counts.warning})` },
    { key: 'safe',     label: `Safe (${counts.safe})` },
  ]

  return (
    <div>
      {/* Header bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
        <div className="flex flex-wrap gap-2">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`px-3.5 py-1.5 rounded-lg text-[13px] font-medium border-[1.5px] transition-all ${
                filter === f.key ? FILTER_STYLES[f.key] : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[12px] text-slate-500">
            Last updated: {lastUpdated ? formatDateTime(lastUpdated) : '—'}
          </span>
          <span className={`text-[11px] font-semibold px-2 py-1 rounded-full ${
            liveConnected ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'
          }`}>
            {liveConnected ? 'Live stream connected' : 'Live stream offline'}
          </span>
          <button 
            onClick={exportCSV} 
            className="btn btn-secondary btn-sm gap-1.5"
          >
            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
            Export Report
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Alerts table */}
      <div className="card overflow-hidden mb-5">
        <div className="overflow-x-auto">
          <table className="w-full data-table">
            <thead><tr>
              <th style={{width:120}}>Severity</th>
              <th>Alert Details</th>
              <th>Location</th>
              <th style={{width:100}}>Time</th>
              <th style={{width:100}}>Action</th>
            </tr></thead>
            <tbody>
              <AnimatePresence mode="popLayout">
                {loading && alerts.length === 0 && (
                  <tr>
                    <td colSpan={5} className="text-center py-12 text-slate-400 text-sm">
                      Loading alert history…
                    </td>
                  </tr>
                )}
                {alerts.map((a) => (
                  <motion.tr
                    key={a.id}
                    layout
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    transition={{ duration: 0.2 }}
                    onClick={() => setConfirmingAlert(a)}
                    className="cursor-pointer hover:bg-slate-50 transition-all"
                  >
                    <td>
                      <Badge variant={a.severity} dot>{a.severity}</Badge>
                    </td>
                    <td>
                      <p className="font-semibold text-slate-800 text-[13.5px]">{a.title}</p>
                      <p className="text-[12px] text-slate-400 mt-0.5">{a.desc}</p>
                    </td>
                    <td className="text-[13px] text-slate-600">{a.location}</td>
                    <td>
                      <span className="font-mono text-[12px] text-slate-500">{a.time}</span>
                    </td>
                    <td>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setConfirmingAlert(a);
                        }}
                        className="text-[12px] text-brand-500 font-semibold hover:text-brand-700 hover:underline transition-colors"
                      >
                        Acknowledge
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </AnimatePresence>
              {!loading && alerts.length === 0 && (
                <tr><td colSpan={5} className="text-center py-12 text-slate-400 text-sm">No alerts for this filter.</td></tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="px-5 py-3 border-t border-slate-100 text-[12px] text-slate-400">
          Showing {alerts.length} of {counts.all} active alerts
        </div>
      </div>

      {/* Bottom widgets */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* System status */}
        <div className="card p-5">
          <p className="text-[13px] font-semibold text-slate-700 mb-4">System Status</p>
          <div className="flex items-center gap-2 mb-4">
            <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse flex-shrink-0"/>
            <span className="text-sm font-semibold text-slate-700">All Systems Operational</span>
          </div>
          <div className="space-y-3">
            {[['Sensors Active','24/24','100%'],['Scan Queue','0 pending','—'],['Network','Connected','—']].map(([k,v,pct])=>(
              <div key={k}>
                <div className="flex justify-between text-[12px] mb-1">
                  <span className="text-slate-500">{k}</span>
                  <span className="font-semibold text-green-600">{v}</span>
                </div>
                {pct === '100%' && (
                  <div className="h-1 bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full w-full bg-green-500 rounded-full"/>
                  </div>
                )}
              </div>
            ))}
          </div>
          <p className="text-[11px] text-slate-400 mt-3">All 24 monitoring zones reporting normal operations.</p>
        </div>

        {/* Live camera */}
        <LiveCamFeed/>

        {/* Trend chart */}
        <div className="card p-5">
          <p className="text-[13px] font-semibold text-slate-700 mb-4">Alert Trend (24h)</p>
          <ResponsiveContainer width="100%" height={140}>
            <AreaChart data={ALERT_TREND_24H} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9"/>
              <XAxis dataKey="time" tick={{ fontSize: 9, fill: '#94a3b8' }}/>
              <YAxis tick={{ fontSize: 9, fill: '#94a3b8' }}/>
              <Tooltip contentStyle={{ fontSize: 11, borderRadius: 8, border: '1px solid #e2e8f0' }}/>
              <Area type="monotone" dataKey="alerts" stroke="#1a6bff" fill="rgba(26,107,255,.08)" strokeWidth={2}/>
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
      {/* Confirmation Modal */}
      <AnimatePresence>
        {confirmingAlert && (
          <AlertConfirmationModal 
            alert={confirmingAlert} 
            onClose={() => setConfirmingAlert(null)} 
            onConfirm={resolveAlert}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

function AlertConfirmationModal({ alert, onClose, onConfirm }) {
  const navigate = useNavigate();
  const processedImage = alert.processedImage;
  const imgUrl = processedImage 
    ? (processedImage.startsWith('http') ? processedImage : `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}${processedImage}`)
    : null;
  const detections = alert.detections || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
      />
      
      {/* Modal Box */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="relative bg-white rounded-3xl overflow-hidden shadow-2xl border border-slate-100 max-w-2xl w-full max-h-[85vh] flex flex-col z-10"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-800 text-lg flex items-center gap-2">
              Confirm Alert Action
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold uppercase ${alert.severity === 'critical' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'}`}>
                {alert.severity}
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Location: {alert.location}</p>
          </div>
          <button 
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-slate-50 hover:bg-slate-100 text-slate-400 hover:text-slate-600 flex items-center justify-center transition-all font-semibold"
          >
            ✕
          </button>
        </div>

        {/* Content (Scrollable) */}
        <div className="p-6 overflow-y-auto space-y-5 flex-1">
          {/* Details Card */}
          <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
            <h4 className="font-bold text-slate-800 text-sm">{alert.title}</h4>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">{alert.desc}</p>
            <div className="flex gap-4 mt-3 text-[11px] text-slate-400">
              <span>Time: {alert.time}</span>
              <span>•</span>
              <span>Camera ID: {alert.location}</span>
            </div>
          </div>

          {/* Alert Image */}
          <div>
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Processed Scanned Feed</h4>
            <div className="bg-slate-50 rounded-2xl overflow-hidden relative min-h-[180px] max-h-[280px] flex items-center justify-center border border-slate-200">
              {imgUrl ? (
                <img src={imgUrl} alt="Alert Feed" className="w-full h-full object-contain max-h-[280px]" />
              ) : (
                <p className="text-slate-400 text-sm">No feed image available</p>
              )}
            </div>
          </div>

          {/* Detections List */}
          {detections.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Detected Hazards ({detections.length})</h4>
              <div className="space-y-2 max-h-36 overflow-y-auto pr-1">
                {detections.map((det, idx) => (
                  <div key={idx} className="flex justify-between items-center p-2.5 rounded-xl border border-slate-100 bg-slate-50 text-xs">
                    <span className="font-semibold text-slate-800">{det.raw_label || det.object_type}</span>
                    <div className="flex gap-2">
                      <span className="text-slate-500 bg-white px-1.5 py-0.5 rounded border border-slate-200">
                        {(det.confidence * 100).toFixed(1)}% Conf
                      </span>
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${det.severity === 'HIGH' ? 'bg-red-50 text-red-600' : 'bg-yellow-50 text-yellow-600'}`}>
                        {det.severity}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-between items-center gap-3">
          <button
            type="button"
            onClick={() => {
              onClose();
              navigate(`/alerts/${alert.id}`);
            }}
            className="px-4 py-2.5 rounded-xl text-xs font-semibold text-brand-600 hover:bg-brand-50 border border-brand-200 transition-all"
          >
            View Full Report
          </button>
          
          <div className="flex gap-2">
            <button 
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl text-xs font-medium text-slate-500 hover:bg-slate-100 transition-all"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={() => {
                onConfirm(alert.id);
                onClose();
              }}
              className="px-5 py-2.5 rounded-xl text-xs font-bold bg-brand-500 hover:bg-brand-600 text-white transition-all shadow-sm"
            >
              Acknowledge & Resolve
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  )
}