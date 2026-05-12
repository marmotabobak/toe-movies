import { useState } from 'react'
import KeywordsField from './KeywordsField'
import { bulkEdit } from '../../api/movies'

export default function BulkEditModal({ ids, onClose, onSaved }) {
  const [genre, setGenre] = useState('')
  const [keywords, setKeywords] = useState([])
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    const patch = {}
    if (genre) patch.genre = genre
    if (keywords.length) patch.keywords = keywords
    if (!Object.keys(patch).length) return
    setSubmitting(true)
    try {
      await bulkEdit(ids, patch)
      onSaved()
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-xl shadow-xl p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Bulk Edit ({ids.length} movies)</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 text-xl leading-none">&times;</button>
        </div>
        <p className="text-sm text-gray-500 mb-4">Only filled fields will be applied to all selected movies.</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-0.5">Genre (overwrite)</label>
            <input className="border rounded px-2 py-1 text-sm w-full" value={genre} onChange={e => setGenre(e.target.value)} />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Keywords (overwrite)</label>
            <KeywordsField value={keywords} onChange={setKeywords} />
          </div>
          <div className="flex gap-3 justify-end pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm rounded bg-gray-100 hover:bg-gray-200">Cancel</button>
            <button type="submit" disabled={submitting} className="px-4 py-2 text-sm rounded bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50">
              {submitting ? 'Saving…' : 'Apply'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
