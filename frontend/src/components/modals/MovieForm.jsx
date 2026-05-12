import { useState, useEffect } from 'react'
import KeywordsField from './KeywordsField'

const FIELDS = [
  { key: 'title', label: 'Russian Title', required: true },
  { key: 'orig_name', label: 'English Title' },
  { key: 'year', label: 'Year', type: 'number' },
  { key: 'duration_min', label: 'Duration (min)', type: 'number' },
  { key: 'genre', label: 'Genre' },
  { key: 'director', label: 'Director' },
  { key: 'actors', label: 'Actors' },
  { key: 'imdb_rating', label: 'IMDB Rating', type: 'number', step: '0.1' },
  { key: 'rt_score', label: 'RT Score %', type: 'number' },
  { key: 'metascore', label: 'Metascore', type: 'number' },
  { key: 'imdb_id', label: 'IMDB ID' },
  { key: 'plot', label: 'Plot', multiline: true },
  { key: 'poster_url', label: 'Poster URL' },
]

export default function MovieForm({ initial = {}, onSubmit, onCancel, submitting }) {
  const [form, setForm] = useState({
    title: '', orig_name: '', year: '', duration_min: '', genre: '',
    director: '', actors: '', imdb_rating: '', rt_score: '', metascore: '',
    imdb_id: '', plot: '', poster_url: '', keywords: [],
    ...initial,
  })

  useEffect(() => { setForm(f => ({ ...f, ...initial })) }, [initial?.id])

  function set(key, val) { setForm(f => ({ ...f, [key]: val })) }

  function handleSubmit(e) {
    e.preventDefault()
    const body = {}
    for (const { key, type } of FIELDS) {
      const v = form[key]
      if (v === '' || v == null) { body[key] = null; continue }
      body[key] = type === 'number' ? Number(v) : v
    }
    body.keywords = form.keywords
    onSubmit(body)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      {FIELDS.map(({ key, label, type, step, required, multiline }) => (
        <div key={key}>
          <label className="block text-xs font-medium text-gray-600 mb-0.5">{label}{required && ' *'}</label>
          {multiline ? (
            <textarea
              className="border rounded px-2 py-1 text-sm w-full resize-none"
              rows={3}
              value={form[key] ?? ''}
              onChange={e => set(key, e.target.value)}
            />
          ) : (
            <input
              className="border rounded px-2 py-1 text-sm w-full"
              type={type || 'text'}
              step={step}
              required={required}
              value={form[key] ?? ''}
              onChange={e => set(key, e.target.value)}
            />
          )}
        </div>
      ))}

      <div>
        <label className="block text-xs font-medium text-gray-600 mb-0.5">Keywords</label>
        <KeywordsField value={form.keywords} onChange={v => set('keywords', v)} />
      </div>

      <div className="flex gap-3 pt-2 justify-end">
        <button type="button" onClick={onCancel} className="px-4 py-2 text-sm rounded bg-gray-100 hover:bg-gray-200">Cancel</button>
        <button type="submit" disabled={submitting} className="px-4 py-2 text-sm rounded bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50">
          {submitting ? 'Saving…' : 'Save'}
        </button>
      </div>
    </form>
  )
}
