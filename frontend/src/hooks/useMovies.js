import { useState, useEffect, useRef } from 'react'
import { fetchMovies } from '../api/movies'

export function useMovies(filters, refetchKey) {
  const [state, setState] = useState({ movies: [], total: 0, totalPages: 1, loading: true, error: null })
  const prev = useRef(null)

  useEffect(() => {
    const key = JSON.stringify(filters) + refetchKey
    if (key === prev.current) return
    prev.current = key

    setState(s => ({ ...s, loading: true, error: null }))
    fetchMovies(filters)
      .then(data => setState({
        movies: data.data,
        total: data.total,
        totalPages: data.total_pages,
        loading: false,
        error: null,
      }))
      .catch(err => setState(s => ({ ...s, loading: false, error: err.message })))
  }, [filters, refetchKey])

  return state
}
