export default function Table({ columns, data, emptyMsg = 'No records found.', loading = false }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 text-slate-400 text-sm gap-2">
        <span className="w-4 h-4 border-2 border-slate-300 border-t-brand-500 rounded-full animate-spin" />
        Loading…
      </div>
    )
  }
  if (!data?.length) {
    return <div className="py-16 text-center text-slate-400 text-sm">{emptyMsg}</div>
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full data-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key} style={{ width: col.width }} className={col.thClass || ''}>
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, ri) => (
            <tr key={row.id ?? ri}>
              {columns.map((col) => (
                <td key={col.key} className={col.tdClass || ''}>
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
