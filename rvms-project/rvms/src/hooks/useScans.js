import { useState, useEffect } from 'react'
import { scanService } from '@/services/api'

export function useScans() {
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    scanService.getRecent().then(({ data }) => {
      setScans(data)
      setLoading(false)
    })
  }, [])

  return { scans, loading }
}
