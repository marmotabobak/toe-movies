import { useState, useEffect } from 'react'
import { fetchGenres } from '../../api/movies'

function useDebounce(value, delay = 400) {
  const [dv, setDv] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDv(value), delay)
    return () => clearTimeout(t)
  }, [value, delay])
  return dv
}

export default function FilterBar({ filters, onChange }) {
  const [q, setQ] = useState(filters.q || '')
  const [genres, setGenres] = useState([])
  const dq = useDebounce(q)

  useEffect(() => { fetchGenres().then(d => setGenres(d.genres)) }, [])
  useEffect(() => { onChange({ q: dq }) }, [dq])

  function set(key, val) { onChange({ [key]: val || undefined }) }

  return (
    <div className="bg-white border-b px-4 py-3 flex flex-wrap gap-3 items-end">
      <div className="flex-1 min-w-[180px]">
        <label className="text-xs text-gray-500 block mb-0.5">Search</label>
        <input
          className="border rounded px-2 py-1.5 text-sm w-full"
          placeholder="Title, director, actors…"
          value={q}
          onChange={e => setQ(e.target.value)}
        />
      </div>

      <div className="min-w-[130px]">
        <label className="text-xs text-gray-500 block mb-0.5">Genre</label>
        <select className="border rounded px-2 py-1.5 text-sm w-full" defaultValue=""
          onChange={e => set('genre', e.target.value)}>
          <option value="">All</option>
          {genres.map(g => <option key={g}>{g}</option>)}
        </select>
      </div>

      <div className="flex gap-2 items-end">
        <div>
          <label className="text-xs text-gray-500 block mb-0.5">Year from</label>
          <input type="number" className="border rounded px-2 py-1.5 text-sm w-20"
            placeholder="1900" onChange={e => set('year_from', e.target.value)} />
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-0.5">to</label>
          <input type="number" className="border rounded px-2 py-1.5 text-sm w-20"
            placeholder="2026" onChange={e => set('year_to', e.target.value)} />
        </div>
      </div>

      <div className="flex gap-2 items-end">
        <div>
          <label className="text-xs text-gray-500 block mb-0.5">IMDB ≥</label>
          <input type="number" step="0.1" className="border rounded px-2 py-1.5 text-sm w-16"
            placeholder="0" onChange={e => set('imdb_min', e.target.value)} />
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-0.5">RT ≥</label>
          <input type="number" className="border rounded px-2 py-1.5 text-sm w-16"
            placeholder="0" onChange={e => set('rt_min', e.target.value)} />
        </div>
      </div>

      <div className="min-w-[130px]">
        <label className="text-xs text-gray-500 block mb-0.5">Keyword</label>
        <input className="border rounded px-2 py-1.5 text-sm w-full"
          placeholder="e.g. horror" onChange={e => set('keyword', e.target.value)} />
      </div>
    </div>
  )
}
