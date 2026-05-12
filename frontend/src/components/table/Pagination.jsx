export default function Pagination({ page, totalPages, onPage }) {
  if (totalPages <= 1) return null

  const pages = []
  const around = 2
  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= page - around && i <= page + around)) pages.push(i)
    else if (pages[pages.length - 1] !== '…') pages.push('…')
  }

  return (
    <div className="flex items-center gap-1 justify-center py-4 flex-wrap">
      <button disabled={page === 1} onClick={() => onPage(page - 1)}
        className="px-3 py-1 text-sm rounded border disabled:opacity-40 hover:bg-gray-50">‹</button>
      {pages.map((p, i) =>
        p === '…'
          ? <span key={`e${i}`} className="px-2 text-gray-400 text-sm">…</span>
          : <button key={p} onClick={() => onPage(p)}
              className={`px-3 py-1 text-sm rounded border ${p === page ? 'bg-blue-600 text-white border-blue-600' : 'hover:bg-gray-50'}`}>
              {p}
            </button>
      )}
      <button disabled={page === totalPages} onClick={() => onPage(page + 1)}
        className="px-3 py-1 text-sm rounded border disabled:opacity-40 hover:bg-gray-50">›</button>
    </div>
  )
}
