// ── SCANS (recent activity) ────────────────────────────────────────────────
export const RECENT_SCANS = [
  { id: '#SCN-8921', ts: '14:25:31', status: 'completed', fod: 'None', runway: '09R', confidence: '99.8%', duration: '1.2s' },
  { id: '#SCN-8920', ts: '14:05:12', status: 'completed', fod: 'None', runway: '27L', confidence: '99.5%', duration: '1.4s' },
  { id: '#SCN-8919', ts: '13:45:00', status: 'flagged',   fod: 'Small Debris', runway: '09R', confidence: '97.2%', duration: '1.1s' },
  { id: '#SCN-8918', ts: '13:25:05', status: 'completed', fod: 'None', runway: '27L', confidence: '99.9%', duration: '1.3s' },
  { id: '#SCN-8917', ts: '12:55:42', status: 'completed', fod: 'None', runway: '09R', confidence: '98.7%', duration: '1.5s' },
  { id: '#SCN-8916', ts: '12:35:18', status: 'flagged',   fod: 'Metal Fragment', runway: '27L', confidence: '95.4%', duration: '1.2s' },
]

// ── ALERTS ────────────────────────────────────────────────────────────────
export const ALERTS_DATA = [
  { id: 1, severity: 'critical', title: 'FOD Detected (Large Object)',      desc: 'High probability of engine ingestion risk.',              location: 'Runway 09R – Zone 4',         time: '14:25:31', action: 'Dispatching ground crew. NOTAM issued.', resolved: false },
  { id: 2, severity: 'warning',  title: 'Runway Lighting Failure',          desc: 'Centerline lights segment B flickering.',                location: 'Runway 27L – Sector 2',       time: '14:21:05', action: 'Engineering notified.',                resolved: false },
  { id: 3, severity: 'warning',  title: 'Surface Crack Detected',           desc: 'Minor expansion joint observed in Zone 3.',              location: 'Taxiway Alpha',               time: '14:18:44', action: 'Logged for maintenance review.',        resolved: false },
  { id: 4, severity: 'safe',     title: 'Routine Inspection Complete',      desc: 'Automated sweep of sector Charlie 4.',                   location: 'Taxiway Charlie',             time: '14:05:12', action: 'Archived.',                            resolved: false },
  { id: 5, severity: 'critical', title: 'Unauthorized Incursion',           desc: 'Unknown vehicle detected on active runway.',             location: 'Runway 09R – Zone 1',         time: '13:58:20', action: 'ATC alerted. Ground stop enacted.',     resolved: false },
  { id: 6, severity: 'warning',  title: 'Rubber Deposit Accumulation',      desc: 'Friction levels approaching safety threshold.',          location: 'Runway 27L – Touchdown Zone', time: '13:45:10', action: 'Scheduled for sweeper crew.',           resolved: false },
  { id: 7, severity: 'warning',  title: 'Sensor Calibration Drift',        desc: 'Camera 14 optical axis offset detected.',                location: 'Runway 09R – Zone 2',         time: '13:30:00', action: 'Auto-recalibration initiated.',         resolved: false },
  { id: 8, severity: 'safe',     title: 'Perimeter Fence Sensor Triggered', desc: 'Wildlife (bird) contact near threshold 09.',             location: 'Threshold 09R',               time: '13:10:55', action: 'Logged. Wildlife officer contacted.',   resolved: false },
]

// ── HISTORY ───────────────────────────────────────────────────────────────
export const HISTORY_SCANS = [
  { id: '#SCN-8921', date: '14 Oct 2023', dateISO: '2023-10-14', time: '14:25:31', runway: '09R', duration: '1.2s', fod: 'None',           status: 'completed', confidence: '99.8%', zones: 4 },
  { id: '#SCN-8920', date: '14 Oct 2023', dateISO: '2023-10-14', time: '14:05:12', runway: '27L', duration: '1.4s', fod: 'None',           status: 'completed', confidence: '99.5%', zones: 4 },
  { id: '#SCN-8919', date: '14 Oct 2023', dateISO: '2023-10-14', time: '13:45:00', runway: '09R', duration: '1.1s', fod: 'Small Debris',   status: 'flagged',   confidence: '97.2%', zones: 4 },
  { id: '#SCN-8918', date: '14 Oct 2023', dateISO: '2023-10-14', time: '13:25:05', runway: '27L', duration: '1.3s', fod: 'None',           status: 'completed', confidence: '99.9%', zones: 4 },
  { id: '#SCN-8917', date: '14 Oct 2023', dateISO: '2023-10-14', time: '12:55:42', runway: '09R', duration: '1.5s', fod: 'None',           status: 'completed', confidence: '98.7%', zones: 4 },
  { id: '#SCN-8916', date: '14 Oct 2023', dateISO: '2023-10-14', time: '12:35:18', runway: '27L', duration: '1.2s', fod: 'Metal Fragment', status: 'flagged',   confidence: '95.4%', zones: 4 },
  { id: '#SCN-8915', date: '13 Oct 2023', dateISO: '2023-10-13', time: '17:10:00', runway: '09R', duration: '1.3s', fod: 'None',           status: 'completed', confidence: '99.1%', zones: 4 },
  { id: '#SCN-8914', date: '13 Oct 2023', dateISO: '2023-10-13', time: '16:50:22', runway: '27L', duration: '1.4s', fod: 'None',           status: 'completed', confidence: '99.6%', zones: 4 },
  { id: '#SCN-8913', date: '13 Oct 2023', dateISO: '2023-10-13', time: '16:30:11', runway: '09R', duration: '1.1s', fod: 'None',           status: 'completed', confidence: '98.9%', zones: 4 },
  { id: '#SCN-8912', date: '13 Oct 2023', dateISO: '2023-10-13', time: '16:10:55', runway: '27L', duration: '1.6s', fod: 'Tire Fragment',  status: 'flagged',   confidence: '96.3%', zones: 4 },
  { id: '#SCN-8911', date: '13 Oct 2023', dateISO: '2023-10-13', time: '15:50:00', runway: '09R', duration: '1.2s', fod: 'None',           status: 'completed', confidence: '99.7%', zones: 4 },
  { id: '#SCN-8910', date: '13 Oct 2023', dateISO: '2023-10-13', time: '15:30:44', runway: '27L', duration: '1.3s', fod: 'None',           status: 'completed', confidence: '99.2%', zones: 4 },
]

// ── CHARTS ────────────────────────────────────────────────────────────────
export const ALERT_TREND_24H = [
  { time: '00:00', alerts: 2 }, { time: '03:00', alerts: 1 }, { time: '06:00', alerts: 4 },
  { time: '09:00', alerts: 7 }, { time: '11:00', alerts: 5 }, { time: '12:00', alerts: 8 },
  { time: '13:00', alerts: 11 }, { time: '14:00', alerts: 12 }, { time: 'Now', alerts: 9 },
]

export const MONTHLY_TREND = [
  { month: 'Aug', scans: 210, flags: 8,  resolved: 7  },
  { month: 'Sep', scans: 234, flags: 12, resolved: 11 },
  { month: 'Oct', scans: 198, flags: 6,  resolved: 6  },
  { month: 'Nov', scans: 245, flags: 15, resolved: 13 },
  { month: 'Dec', scans: 267, flags: 9,  resolved: 9  },
  { month: 'Jan', scans: 289, flags: 11, resolved: 10 },
]

export const SYSTEM_HEALTH = [
  { name: 'Cameras',     total: 24, active: 24, icon: '📷' },
  { name: 'LIDAR',       total: 8,  active: 8,  icon: '📡' },
  { name: 'Thermal',     total: 6,  active: 4,  icon: '🌡️' },
  { name: 'Radar',       total: 4,  active: 4,  icon: '📶' },
]

export const SEARCH_RESULTS = [
  { icon: '🔍', label: 'SCN-8919 — Small Debris FOD', type: 'Scan' },
  { icon: '⚠️', label: 'Critical: FOD Detected (Large Object)', type: 'Alert' },
  { icon: '📋', label: 'Runway 09R Inspection Log', type: 'History' },
  { icon: '⚙️', label: 'Sensor Calibration Settings', type: 'Settings' },
]
