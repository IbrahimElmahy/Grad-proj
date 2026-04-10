import { useState, useMemo } from 'react'

export function usePagination(items = [], perPage = 8) {
  const [page, setPage] = useState(1)
  const totalPages = Math.max(1, Math.ceil(items.length / perPage))
  const paged = useMemo(
    () => items.slice((page - 1) * perPage, page * perPage),
    [items, page, perPage]
  )
  const goTo = (p) => setPage(Math.min(Math.max(1, p), totalPages))
  return { paged, page, totalPages, goTo, setPage }
}
