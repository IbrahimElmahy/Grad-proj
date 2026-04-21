import { useEffect, useRef, useState } from 'react'
import ReconnectingWebSocket from 'reconnecting-websocket'
import './App.css'

const DEFAULT_WS_URL = 'ws://127.0.0.1:8000/ws/alerts/'

function severityClass(level) {
  const normalized = String(level || '').toLowerCase()
  if (normalized.includes('high')) return 'high'
  if (normalized.includes('medium')) return 'medium'
  if (normalized.includes('low')) return 'low'
  return 'info'
}

function App() {
  const [connectionState, setConnectionState] = useState('connecting')
  const [alerts, setAlerts] = useState([])
  const [rawMessages, setRawMessages] = useState([])
  const socketRef = useRef(null)

  useEffect(() => {
    const socket = new ReconnectingWebSocket(DEFAULT_WS_URL, [], {
      maxRetries: Infinity,
      reconnectInterval: 1500,
    })
    socketRef.current = socket

    socket.addEventListener('open', () => setConnectionState('connected'))
    socket.addEventListener('close', () => setConnectionState('disconnected'))
    socket.addEventListener('error', () => setConnectionState('error'))
    socket.addEventListener('message', (event) => {
      try {
        const payload = JSON.parse(event.data)
        setRawMessages((current) => [payload, ...current].slice(0, 10))
        if (payload.type === 'hazard.alert') {
          setAlerts((current) => [payload, ...current].slice(0, 25))
        }
      } catch (error) {
        setRawMessages((current) => [
          { type: 'parse.error', message: String(error), raw: event.data },
          ...current,
        ].slice(0, 10))
      }
    })

    return () => {
      socket.close()
    }
  }, [])

  const latestAlert = alerts[0] ?? null
  const latestDetection = latestAlert?.detections?.[0] ?? null

  return (
    <main className="app-shell">
      <div className="dashboard">
        <section className="hero-panel">
          <h1>Runway Alerts Dashboard</h1>
          <p>
            Live alert stream for high-severity runway hazards. The dashboard
            listens to the Django Channels endpoint at <code>{DEFAULT_WS_URL}</code>
            {' '}and shows the most recent detections immediately.
          </p>
        </section>

        <section className="status-panel">
          <div className="status-grid">
            <div className="status-card">
              <div className="status-label">WebSocket</div>
              <div className={`status-value ${connectionState === 'connected' ? 'connected' : 'disconnected'}`}>
                {connectionState}
              </div>
            </div>
            <div className="status-card">
              <div className="status-label">Alerts Received</div>
              <div className="status-value">{alerts.length}</div>
            </div>
            <div className="status-card">
              <div className="status-label">Latest Camera</div>
              <div className="status-value">{latestAlert?.camera_id ?? 'Waiting...'}</div>
            </div>
            <div className="status-card">
              <div className="status-label">Latest Severity</div>
              <div className={`status-value ${severityClass(latestDetection?.hazard_severity)}`}>
                {latestDetection?.hazard_severity ?? 'None'}
              </div>
            </div>
          </div>
        </section>

        <section className="alerts-panel">
          <div className="panel-head">
            <h2>Incoming Alerts</h2>
            <span>Most recent 25</span>
          </div>

          {alerts.length === 0 ? (
            <div className="empty-state">
              No hazard alerts received yet. Start Daphne, connect the backend,
              and send a trigger to see live data here.
            </div>
          ) : (
            <div className="alerts-list">
              {alerts.map((alert, index) => {
                const detection = alert.detections?.[0]
                return (
                  <article className="alert-card" key={`${alert.inspection_id}-${index}`}>
                    <div className="alert-top">
                      <div>
                        <div className="alert-title">
                          {detection?.raw_label ?? 'Unknown Hazard'}
                        </div>
                        <div className="alert-meta">
                          Inspection {alert.inspection_id} • Camera {alert.camera_id} • {alert.timestamp}
                        </div>
                      </div>

                      <div className="alert-badges">
                        <span className={`badge ${severityClass(detection?.hazard_severity)}`}>
                          {detection?.hazard_severity ?? 'Unknown'}
                        </span>
                        <span className="badge info">
                          Track {detection?.track_id ?? 'N/A'}
                        </span>
                      </div>
                    </div>

                    <div className="detection-grid">
                      <div className="metric-box">
                        <strong>Object Type</strong>
                        <span>{detection?.object_type ?? 'N/A'}</span>
                      </div>
                      <div className="metric-box">
                        <strong>Confidence</strong>
                        <span>{detection?.confidence ?? 'N/A'}</span>
                      </div>
                      <div className="metric-box">
                        <strong>Frame</strong>
                        <span>{detection?.frame_index ?? 'N/A'}</span>
                      </div>
                      <div className="metric-box">
                        <strong>BBox</strong>
                        <span>
                          {detection?.bbox_xyxy
                            ? `${detection.bbox_xyxy.x1}, ${detection.bbox_xyxy.y1}, ${detection.bbox_xyxy.x2}, ${detection.bbox_xyxy.y2}`
                            : 'N/A'}
                        </span>
                      </div>
                      <div className="metric-box">
                        <strong>Suggestion</strong>
                        <span>{detection?.gemini_suggestion ?? 'N/A'}</span>
                      </div>
                      <div className="metric-box">
                        <strong>Status</strong>
                        <span>{alert.inspection_status}</span>
                      </div>
                    </div>
                  </article>
                )
              })}
            </div>
          )}
        </section>

        <section className="json-panel">
          <div className="panel-head">
            <h2>Raw WebSocket Payloads</h2>
            <span>Most recent 10</span>
          </div>
          <div className="json-body">
            <pre>{JSON.stringify(rawMessages, null, 2)}</pre>
          </div>
        </section>
      </div>
    </main>
  )
}

export default App
