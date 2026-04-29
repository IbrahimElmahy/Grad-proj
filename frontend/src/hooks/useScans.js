import { useState, useEffect } from 'react'
import { scanService } from '@/services/api'

export function useScans() {
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const refresh = async () => {
    setLoading(true)
    setError('')
    try {
      const { data } = await scanService.getRecent()
      setScans(data)
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to load inspections.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  return { scans, loading, error, refresh }
}
