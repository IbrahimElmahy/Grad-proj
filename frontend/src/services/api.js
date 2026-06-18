import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
})

const MOCK_LOGIN = {
  token: 'mock-jwt-token-rvms-2026',
  user: { name: 'Captain Miller', role: 'Safety Officer' },
}

const DEMO_USERS = {
  'manager@rvms.com': {
    password: 'manager123',
    token: 'mock-jwt-token-rvms-manager',
    user: { name: 'RVMS Manager', role: 'Manager' },
  },

  'officer@rvms.com': {
    password: 'officer123',
    token: 'mock-jwt-token-rvms-officer',
    user: { name: 'Safety Officer', role: 'Safety Officer' },
  },
}

const RISK_TO_ALERT = {
  HIGH: 'critical',
  MEDIUM: 'warning',
  LOW: 'warning',
  SAFE: 'safe',
}

const STATUS_TO_SCAN = {
  ALERT: 'flagged',
  COMPLETED: 'completed',
  PROCESSING: 'pending',
}

function formatTime(value) {
  if (!value) return '—'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return '—'

  return date.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

function formatDateTime(value) {
  if (!value) return '—'

  const normalized = String(value).includes('T')
    ? value
    : String(value).replace(' ', 'T')

  const date = new Date(normalized)

  if (Number.isNaN(date.getTime())) return value

  return date.toLocaleString([], {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

function formatRelativeTime(value) {
  if (!value) return 'No inspections yet'

  const normalized = String(value).includes('T')
    ? value
    : String(value).replace(' ', 'T')

  const date = new Date(normalized)

  if (Number.isNaN(date.getTime())) return value

  const diffMs = Date.now() - date.getTime()
  const diffMinutes = Math.max(0, Math.round(diffMs / 60000))

  if (diffMinutes < 1) return 'Just now'

  if (diffMinutes < 60) {
    return `${diffMinutes} min${diffMinutes === 1 ? '' : 's'} ago`
  }

  const diffHours = Math.round(diffMinutes / 60)

  if (diffHours < 24) {
    return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`
  }

  const diffDays = Math.round(diffHours / 24)

  return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`
}

function getPrimaryDetection(inspection) {
  return (
    inspection?.images
      ?.flatMap((image) => image.detected_objects || [])?.[0] || null
  )
}

function getDetectionCount(inspection) {
  return (
    inspection?.images?.reduce(
      (count, image) => count + (image.detected_objects?.length || 0),
      0
    ) || 0
  )
}

function getDetectionSummary(inspection) {
  const primaryDetection = getPrimaryDetection(inspection)

  if (!primaryDetection) return 'None'

  const totalDetections = getDetectionCount(inspection)

  if (totalDetections <= 1) {
    return (
      primaryDetection.raw_label ||
      primaryDetection.object_type ||
      'Detected object'
    )
  }

  return `${
    primaryDetection.raw_label ||
    primaryDetection.object_type ||
    'Hazard'
  } +${totalDetections - 1} more`
}

function getConfidence(inspection) {
  const confidences =
    inspection?.images
      ?.flatMap((image) => image.detected_objects || [])
      .map((item) => item.confidence) || []

  if (!confidences.length) return '—'

  const maxConfidence = Math.max(...confidences)

  return `${(maxConfidence * 100).toFixed(1)}%`
}

export function mapInspectionToScan(inspection) {
  return {
    id: inspection.id,

    scanLabel: `SCN-${String(inspection.id)
      .slice(0, 8)
      .toUpperCase()}`,

    ts: formatTime(inspection.timestamp),

    timestamp: inspection.timestamp,

    status: STATUS_TO_SCAN[inspection.status] || 'info',

    fod: getDetectionSummary(inspection),

    runway: inspection.camera_id || 'Unknown Camera',

    confidence: getConfidence(inspection),

    duration: 'AI processed',

    riskLevel: inspection.risk_level,

    detectionCount: getDetectionCount(inspection),

    processedVideo: inspection.processed_video || null,

    source: inspection,
  }
}

export function mapInspectionToAlert(inspection) {
  const primaryDetection = getPrimaryDetection(inspection)

  const riskLevel = inspection.risk_level || 'SAFE'

  const severity = RISK_TO_ALERT[riskLevel] || 'safe'

  const detectionCount = getDetectionCount(inspection)

  const safeInspection = riskLevel === 'SAFE'

  return {
    id: inspection.id,

    severity,

    riskLevel,

    title: safeInspection
      ? 'Routine Inspection Complete'
      : `${
          primaryDetection?.raw_label ||
          primaryDetection?.object_type ||
          'Runway Hazard'
        } Detected`,

    desc: safeInspection
      ? `No hazards detected in ${
          inspection.camera_id || 'this inspection'
        }.`
      : primaryDetection?.gemini_suggestion ||
        `Detected ${detectionCount} object${
          detectionCount === 1 ? '' : 's'
        } requiring review.`,

    location: inspection.camera_id || 'Unknown Camera',

    time: formatTime(inspection.timestamp),

    timestamp: inspection.timestamp,

    action:
      inspection.status === 'ALERT'
        ? 'Immediate attention required.'
        : 'Logged for monitoring.',

    resolved: false,

    inspectionStatus: inspection.status,

    detectionCount,

    processedImage:
      inspection.images?.find((image) => image.processed_image)
        ?.processed_image ||
      inspection.images?.find((image) => image.image)?.image ||
      null,

    detections:
      inspection.images?.flatMap(
        (image) => image.detected_objects || []
      ) || [],

    processedVideo: inspection.processed_video || null,

    source: inspection,
  }
}

function buildWebSocketUrl(pathname) {
  const explicitBase = import.meta.env.VITE_WS_BASE_URL

  if (explicitBase) {
    return `${explicitBase.replace(/\/$/, '')}${pathname}`
  }

  const protocol =
    window.location.protocol === 'https:' ? 'wss:' : 'ws:'

  return `${protocol}//${window.location.host}${pathname}`
}

export const authService = {
  login: async (email, password) => {
    try {
      const response = await api.post('/auth/login/', {
        email,
        password,
      })

      return response
    } catch (error) {
      const demoUser =
        DEMO_USERS[email?.trim().toLowerCase()]

      if (demoUser && demoUser.password === password) {
        return {
          data: {
            token: demoUser.token,
            user: {
              ...demoUser.user,
              email,
            },
          },
        }
      }

      if (error?.response) throw error

      return {
        data: {
          ...MOCK_LOGIN,
          email,
        },
      }
    }
  },

  forgotPassword: async (email) => {
    const response = await api.post(
      '/auth/forgot-password/',
      { email }
    )

    return response
  },

  resetPassword: async ({
    token,
    password,
    password_confirm,
  }) => {
    const response = await api.post(
      '/auth/reset-password/',
      {
        token,
        password,
        password_confirm,
      }
    )

    return response
  },
}

export const inspectionService = {
  list: async () => {
    const response = await api.get('/inspections/')

    return response
  },

  detail: async (id) => {
    const response = await api.get(`/inspections/${id}/`)

    return response
  },

  upload: async (formData) => {
    const response = await api.post(
      '/upload/',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 180000,
      }
    )

    return response
  },
}

export const scanService = {
  getRecent: async () => {
    const response = await inspectionService.list()

    return {
      ...response,
      data: response.data.map(mapInspectionToScan),
    }
  },

  initiateScan: async ({ file, cameraId }) => {
    const formData = new FormData()

    formData.append(
      'camera_id',
      cameraId || 'Manual Upload'
    )

    if (file?.type?.startsWith('video/')) {
      formData.append('video', file)
    } else {
      formData.append('image', file)
    }

    const response = await inspectionService.upload(formData)

    return {
      ...response,
      data: mapInspectionToScan(response.data),
      raw: response.data,
    }
  },
}

export const alertsService = {
  getAll: async () => {
    const response = await inspectionService.list()

    return {
      ...response,
      data: response.data.map(mapInspectionToAlert),
    }
  },

  connectLive: ({
    onAlert,
    onOpen,
    onClose,
    onError,
  } = {}) => {
    const socket = new WebSocket(
      buildWebSocketUrl('/ws/alerts/')
    )

    socket.onopen = () => {
      if (onOpen) onOpen()
    }

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data)

      if (payload.type === 'connection.established')
        return

      if (payload.type === 'pong') return

      if (
        payload.type === 'hazard.alert' &&
        onAlert
      ) {
        onAlert({
          id: payload.inspection_id,

          severity:
            RISK_TO_ALERT[
              payload.inspection_risk_level
            ] || 'safe',

          riskLevel: payload.inspection_risk_level,

          title:
            payload.detections?.[0]?.raw_label ||
            payload.detections?.[0]?.object_type
              ? `${
                  payload.detections?.[0]?.raw_label ||
                  payload.detections?.[0]?.object_type
                } Detected`
              : 'Runway Hazard Detected',

          desc:
            payload.detections?.[0]
              ?.gemini_suggestion ||
            `Detected ${
              payload.critical_detection_count || 0
            } critical object(s).`,

          location:
            payload.camera_id || 'Unknown Camera',

          time: formatTime(payload.timestamp),

          timestamp: payload.timestamp,

          action:
            'Live alert received from inspection pipeline.',

          resolved: false,

          inspectionStatus:
            payload.inspection_status,

          detectionCount:
            payload.critical_detection_count || 0,

          processedImage:
            payload.detections?.[0]
              ?.processed_image_path
              ? `/media/${payload.detections[0].processed_image_path}`
              : null,

          detections: payload.detections || [],

          source: payload,

          isLive: true,
        })
      }
    }

    socket.onclose = () => {
      if (onClose) onClose()
    }

    socket.onerror = (error) => {
      if (onError) onError(error)
    }

    return socket
  },
}

export const historyService = {
  getScans: async () => {
    const response = await inspectionService.list()

    return {
      ...response,
      data: response.data.map(mapInspectionToScan),
    }
  },
}

export { formatDateTime, formatRelativeTime }

export default api