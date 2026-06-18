import { useMemo, useRef, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { useAppStore } from '@/store/appStore'
import { useScans } from '@/hooks/useScans'
import StatCard from '@/components/ui/StatCard'
import Badge from '@/components/ui/Badge'
import { ALERT_TREND_24H } from '@/data/mockData'
import { formatDateTime, formatRelativeTime, scanService } from '@/services/api'

function ScanHero({ onRefresh, onScanComplete }) {
  const { scanning, scanProgress, startScan } = useAppStore()
  const [lastResult, setLastResult] = useState(null)
  const [uploadError, setUploadError] = useState('')
  const [uploadingName, setUploadingName] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [previewFile, setPreviewFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const fileInputRef = useRef(null)

  const handleScanClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }

    setPreviewFile(file)
    setPreviewUrl(URL.createObjectURL(file))
    setLastResult(null)
    setUploadError('')
    setUploadingName(file.name)
    setIsUploading(true)
    startScan()

    try {
      const { data } = await scanService.initiateScan({ file, cameraId: 'Manual Upload' })
      setLastResult(data)
      await onRefresh()
      if (onScanComplete) {
        onScanComplete(data)
      }
    } catch (error) {
      setUploadError(error?.response?.data?.error || error?.message || 'Upload failed.')
    } finally {
      event.target.value = ''
      setUploadingName('')
      setIsUploading(false)
    }
  }

  return (
    <motion.div
      className="relative rounded-2xl overflow-hidden mb-6"
      style={{
        backgroundImage: 'url(../src/imgs/hero-pic.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      {/* dark overlay so text stays readable */}
      <div className="absolute inset-0 bg-slate-900/70" />

      <div className="relative z-10 flex flex-col md:flex-row items-stretch md:items-center gap-6 p-7">
        <div className="flex-1">
          <span className="inline-block bg-brand-500/20 text-brand-300 text-[10px] font-bold tracking-widest uppercase px-3 py-1 rounded-full border border-brand-500/20 mb-3">
            Manual Override
          </span>
          <h2 className="text-white text-2xl font-bold mb-2">Initiate Manual Scan</h2>
          <p className="text-white/55 text-sm leading-relaxed max-w-lg">
            Deploy high-precision camera-based runway surveillance for foreign object debris (FOD) and potential hazards. Manual scans override automated schedules for immediate situational awareness.
          </p>

          <div className="flex flex-wrap gap-3 mt-5">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,video/*"
              onChange={handleFileChange}
              className="hidden"
            />
            <motion.button
              whileTap={{ scale: 0.97 }}
              onClick={handleScanClick}
              disabled={scanning || isUploading}
              className="flex items-center gap-2 bg-brand-500 hover:bg-brand-600 disabled:opacity-70 text-white px-5 py-2.5 rounded-xl text-[14px] font-semibold transition-all shadow-lg shadow-brand-500/25"
            >
              {scanning || isUploading ? (
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"/>
              ) : (
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
              )}
              {scanning || isUploading ? 'Uploading & scanning…' : 'Upload Image / Video Scan'}
            </motion.button>
            <button className="flex items-center gap-2 bg-white/10 hover:bg-white/15 text-white/80 px-5 py-2.5 rounded-xl text-[14px] font-medium border border-white/15 transition-all">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/>
              </svg>
              Configuration
            </button>
          </div>

          {/* Scan progress bar */}
          <AnimatePresence>
            {(scanning || isUploading) && (
              <motion.div
                className="mt-4 max-w-sm"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
              >
                <div className="flex justify-between text-[11px] text-white/50 mb-1">
                  <span>{uploadingName ? `Processing ${uploadingName}...` : 'Scanning zones…'}</span>
                  <span>{scanProgress}%</span>
                </div>
                <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-brand-400 rounded-full"
                    animate={{ width: `${scanProgress}%` }}
                    transition={{ duration: 0.1 }}
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Last result chip */}
          <AnimatePresence>
            {lastResult && (
              <motion.div
                className="mt-3 inline-flex items-center gap-2 bg-green-500/15 border border-green-500/25 text-green-300 text-[12px] px-3 py-1.5 rounded-full"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-green-400"/>
                {lastResult.scanLabel} complete · Confidence {lastResult.confidence} · {lastResult.fod}
              </motion.div>
            )}
          </AnimatePresence>
          {uploadError && (
            <p className="mt-3 text-[12px] text-red-200 bg-red-500/10 border border-red-400/20 rounded-lg px-3 py-2 max-w-lg">
              {uploadError}
            </p>
          )}
        </div>

        {/* Local Preview Area */}
        {previewUrl && (
          <div className="w-full md:w-80 h-48 bg-slate-950/90 rounded-2xl overflow-hidden border border-white/15 relative flex items-center justify-center shadow-xl">
            {previewFile?.type?.startsWith('video/') ? (
              <video
                src={previewUrl}
                controls
                className="w-full h-full object-contain"
                autoPlay
                muted
              />
            ) : (
              <img
                src={previewUrl}
                alt="Upload Preview"
                className="w-full h-full object-contain"
              />
            )}

            {/* AI Analyzing Pulsing Badge */}
            {(scanning || isUploading) && (
              <div className="absolute top-3 right-3 bg-brand-500/90 text-white text-[10px] font-bold tracking-wider uppercase px-2.5 py-1 rounded-full flex items-center gap-1.5 shadow-md animate-pulse">
                <span className="w-1.5 h-1.5 rounded-full bg-white animate-ping" />
                AI Analyzing
              </div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  )
}

function ActivityFeed({ scans, loading, onSelectScan }) {
  return (
    <div className="card overflow-hidden">
      <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
        <h3 className="font-semibold text-slate-800">System Activity Feed</h3>
        <Link to="/history" className="text-brand-500 text-[13px] font-medium hover:underline">View All Logs</Link>
      </div>
      {loading ? (
        <div className="flex justify-center py-8">
          <span className="w-5 h-5 border-2 border-slate-200 border-t-brand-500 rounded-full animate-spin"/>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full data-table">
            <thead><tr>
              <th>Scan ID</th><th>Timestamp</th><th>Status</th><th>FOD Detected</th>
            </tr></thead>
            <tbody>
              {scans.map((s) => (
                <tr 
                  key={s.id} 
                  onClick={() => onSelectScan(s)} 
                  className="cursor-pointer hover:bg-slate-50 transition-all"
                  title="Click to view details"
                >
                  <td><span className="font-mono text-[12px] text-brand-500 font-bold">{s.scanLabel}</span></td>
                  <td><span className="font-mono text-[12px] text-slate-500">{s.ts}</span></td>
                  <td><Badge variant={s.status} dot>{s.status}</Badge></td>
                  <td>
                    {s.fod === 'None'
                      ? <span className="text-slate-400 text-[13px]">—</span>
                      : <span className="text-red-600 font-semibold text-[13px]">{s.fod}</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function RightWidgets({ scans }) {
  const alertsToday = useMemo(
    () => scans.filter((scan) => scan.status === 'flagged').length,
    [scans]
  )
  const resolvedAlerts = useMemo(
    () => scans.filter((scan) => scan.status === 'completed').length,
    [scans]
  )
  const latestScan = scans[0]
  const resolutionRate = scans.length ? Math.round((resolvedAlerts / scans.length) * 100) : 0

  return (
    <div className="flex flex-col gap-4">
      {/* Alerts today */}
      <div className="card p-5">
        <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5 mb-3">
          <span className="w-1.5 h-1.5 rounded-full bg-red-500"/>Alerts Detected Today
        </p>
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-extrabold text-slate-900">{alertsToday}</span>
          <span className="text-[12px] bg-red-100 text-red-700 font-semibold px-2 py-0.5 rounded-full">
            Live from inspection history
          </span>
        </div>
      </div>

      {/* Resolved */}
      <div className="card p-5">
        <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5 mb-3">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500"/>Resolved Alerts
        </p>
        <span className="text-4xl font-extrabold text-slate-900">{resolvedAlerts}</span>
        <div className="mt-3 h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div className="h-full bg-green-500 rounded-full" style={{ width: `${resolutionRate}%` }}/>
        </div>
        <p className="text-[11px] text-slate-400 mt-1.5">{resolutionRate}% completion rate</p>
      </div>

      {/* Last scan result */}
      <div className="card p-5">
        <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
          Last Scan Result
        </p>
        {[
          ['Confidence Score', latestScan?.confidence || '—'],
          ['Inspection Time', latestScan?.ts || '—'],
          ['Camera ID', latestScan?.runway || '—'],
          ['FOD', latestScan?.fod || '—'],
        ].map(([k,v])=>(
          <div key={k} className="flex justify-between text-[13px] py-1.5 border-b border-slate-100 last:border-0">
            <span className="text-slate-500">{k}</span>
            <span className="font-semibold text-slate-800">{v}</span>
          </div>
        ))}
        <div className={`mt-3 rounded-xl p-2.5 text-[12px] font-medium ${
          latestScan?.status === 'flagged'
            ? 'bg-red-50 border border-red-200 text-red-700'
            : 'bg-green-50 border border-green-200 text-green-700'
        }`}>
          {latestScan?.status === 'flagged'
            ? 'Alert detected in the latest inspection and is ready for review.'
            : 'No critical hazard was reported in the latest inspection.'}
        </div>
      </div>

      {/* Alert trend mini chart */}
      <div className="card p-5">
        <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-3">Alert Trend (24h)</p>
        <ResponsiveContainer width="100%" height={90}>
          <AreaChart data={ALERT_TREND_24H} margin={{ top: 2, right: 2, bottom: 0, left: -28 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9"/>
            <XAxis dataKey="time" tick={{ fontSize: 9, fill: '#94a3b8' }}/>
            <YAxis tick={{ fontSize: 9, fill: '#94a3b8' }}/>
            <Tooltip contentStyle={{ fontSize: 11, borderRadius: 8, border: '1px solid #e2e8f0' }}/>
            <Area type="monotone" dataKey="alerts" stroke="#1a6bff" fill="rgba(26,107,255,.08)" strokeWidth={2}/>
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

function ScanDetailsModal({ scan, onClose }) {
  const navigate = useNavigate();
  const isAlert = scan.status === 'flagged' || scan.status === 'ALERT';
  const raw = scan.source;
  const processedVideo = scan.processedVideo || raw?.processed_video;
  const videoUrl = processedVideo 
    ? (processedVideo.startsWith('http') ? processedVideo : `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}${processedVideo}`)
    : null;
  const processedImage = raw?.images?.[0]?.processed_image || raw?.images?.[0]?.image;
  const imgUrl = processedImage 
    ? (processedImage.startsWith('http') ? processedImage : `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}${processedImage}`)
    : null;
  const detections = raw?.images?.flatMap(i => i.detected_objects || []) || [];

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
              Scan Details: {scan.scanLabel}
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold uppercase ${isAlert ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                {scan.riskLevel || (isAlert ? 'HIGH' : 'SAFE')}
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Location: {scan.runway}</p>
          </div>
          <button 
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-slate-50 hover:bg-slate-100 text-slate-400 hover:text-slate-600 flex items-center justify-center transition-all font-semibold"
          >
            ✕
          </button>
        </div>

        {/* Content (Scrollable) */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {/* Scanned Feed */}
          <div>
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
              {videoUrl ? "Scanned Feed Video" : "Scanned Feed Image"}
            </h4>
            <div className="bg-slate-50 rounded-2xl overflow-hidden relative min-h-[200px] max-h-[300px] flex items-center justify-center border border-slate-200">
              {videoUrl ? (
                <video src={videoUrl} controls autoPlay loop muted className="w-full h-full object-contain max-h-[300px]" />
              ) : imgUrl ? (
                <img src={imgUrl} alt="Inspection Feed" className="w-full h-full object-contain max-h-[300px]" />
              ) : (
                <p className="text-slate-400 text-sm">No feed media available</p>
              )}
            </div>
          </div>

          {/* Detections */}
          <div>
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Detected Objects & Issues</h4>
            <div className="space-y-3">
              {detections.length > 0 ? (
                detections.map((det, idx) => (
                  <div key={idx} className="flex items-start gap-4 p-4 rounded-2xl border border-slate-100 bg-slate-50">
                    <div className="w-9 h-9 rounded-full bg-white flex items-center justify-center flex-shrink-0 text-md shadow-sm border border-slate-100">
                      {det.severity === 'HIGH' ? '⚠️' : '🔍'}
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between items-start">
                        <h5 className="font-semibold text-slate-800 text-sm">{det.raw_label || det.object_type}</h5>
                        <span className="text-[11px] font-medium text-slate-500 bg-white px-2 py-0.5 rounded-md border border-slate-200">
                          {(det.confidence * 100).toFixed(1)}% Conf
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 mt-1">{det.gemini_suggestion || 'No suggestion available.'}</p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-4 bg-green-50/50 border border-green-100 rounded-2xl text-green-700 text-xs flex items-center gap-2">
                  <span>✓</span> No hazards or debris detected in this scan.
                </div>
              )}
            </div>
          </div>

          {/* Meta Grid */}
          <div className="grid grid-cols-2 gap-4 border-t border-slate-100 pt-4">
            <div>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Timestamp</span>
              <p className="text-sm font-medium text-slate-700 mt-0.5">{formatDateTime(scan.timestamp)}</p>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">System Status</span>
              <p className="text-sm font-medium text-slate-700 mt-0.5 capitalize">{scan.status}</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end gap-3">
          <button 
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-sm font-medium text-slate-500 hover:bg-slate-100 transition-all"
          >
            Close
          </button>
          <button
            type="button"
            onClick={() => {
              onClose();
              navigate(`/alerts/${scan.id}`);
            }}
            className="px-4 py-2 rounded-xl text-sm font-semibold bg-brand-500 hover:bg-brand-600 text-white transition-all shadow-sm"
          >
            View Full Report
          </button>
        </div>
      </motion.div>
    </div>
  );
}

export default function DashboardPage() {
  const { scans, loading, error, refresh } = useScans()
  const [selectedScan, setSelectedScan] = useState(null)
  const latestScan = scans[0]
  const flaggedCount = scans.filter((scan) => scan.status === 'flagged').length
  const runwayStatus = flaggedCount > 0 ? 'Alert' : 'Safe'
  const runwaySub = latestScan
    ? `${latestScan.runway} · ${latestScan.fod === 'None' ? 'clear' : latestScan.fod}`
    : 'Waiting for inspections'
  const systemHealth = scans.length ? 'Connected' : 'Awaiting Data'
  const healthSub = scans.length
    ? `${scans.length} inspection${scans.length === 1 ? '' : 's'} loaded`
    : 'Backend history not loaded yet'

  return (
    <div>
      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <StatCard
          label="Runway Status"
          value={runwayStatus}
          sub={runwaySub}
          valueColor={runwayStatus === 'Alert' ? 'text-red-600' : 'text-green-600'}
          iconBg={runwayStatus === 'Alert' ? 'bg-red-50' : 'bg-green-50'}
          delay={0}
          icon={<svg className={`w-6 h-6 ${runwayStatus === 'Alert' ? 'text-red-600' : 'text-green-600'}`} fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>}
        />
        <StatCard
          label="Last Inspection"
          value={formatRelativeTime(latestScan?.timestamp)}
          sub={latestScan ? `${latestScan.scanLabel} · ${latestScan.status}` : 'No inspections yet'}
          iconBg="bg-brand-50"
          delay={0.05}
          icon={<svg className="w-6 h-6 text-brand-500" fill="currentColor" viewBox="0 0 24 24"><path d="M13 3a9 9 0 0 0-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42A8.954 8.954 0 0 0 13 21a9 9 0 0 0 0-18zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/></svg>}
        />
        <StatCard
          label="System Health"
          value={systemHealth}
          sub={healthSub}
          valueColor="text-purple-600"
          iconBg="bg-purple-50"
          delay={0.1}
          icon={<svg className="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 24 24"><path d="M17 12h-5v5h5v-5zM16 1v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-1V1h-2zm3 18H5V8h14v11z"/></svg>}
        />
      </div>

      <ScanHero onRefresh={refresh} onScanComplete={setSelectedScan} />

      {error && (
        <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}
      {latestScan && (
        <div className="mb-6 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
          Latest backend inspection: <span className="font-semibold text-slate-800">{latestScan.scanLabel}</span> at{' '}
          <span className="font-mono">{formatDateTime(latestScan.timestamp)}</span>
        </div>
      )}

      {/* Bottom grid */}
      <div className="grid grid-cols-1 xl:grid-cols-[1fr_300px] gap-5">
        <ActivityFeed scans={scans} loading={loading} onSelectScan={setSelectedScan}/>
        <RightWidgets scans={scans}/>
      </div>

      {/* Details Modal */}
      <AnimatePresence>
        {selectedScan && (
          <ScanDetailsModal scan={selectedScan} onClose={() => setSelectedScan(null)} />
        )}
      </AnimatePresence>
    </div>
  )
}
