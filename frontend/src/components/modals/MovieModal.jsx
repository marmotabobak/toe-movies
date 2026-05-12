import { useState, useEffect } from 'react'
import { fetchMovie, createMovie, updateMovie } from '../../api/movies'
import MovieForm from './MovieForm'
import Spinner from '../common/Spinner'

export default function MovieModal({ movieId, onClose, onSaved }) {
  const isEdit = movieId != null
  const [movie, setMovie] = useState(null)
  const [loading, setLoading] = useState(isEdit)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!isEdit) return
    setLoading(true)
    fetchMovie(movieId).then(m => { setMovie(m); setLoading(false) })
  }, [movieId])

  async function handleSubmit(body) {
    setSubmitting(true)
    try {
      if (isEdit) await updateMovie(movieId, body)
      else await createMovie(body)
      onSaved()
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-40 flex items-start justify-center bg-black/40 overflow-y-auto py-8">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl mx-4 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">{isEdit ? 'Edit Movie' : 'Add Movie'}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 text-xl leading-none">&times;</button>
        </div>
        {loading ? <Spinner /> : (
          <MovieForm initial={movie || {}} onSubmit={handleSubmit} onCancel={onClose} submitting={submitting} />
        )}
      </div>
    </div>
  )
}
