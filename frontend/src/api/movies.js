const BASE = '/api/movies'

async function req(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

export const fetchMovies = (params) => {
  const qs = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v !== null && v !== undefined && v !== ''))
  ).toString()
  return req(`${BASE}${qs ? '?' + qs : ''}`)
}

export const fetchMovie = (id) => req(`${BASE}/${id}`)
export const fetchGenres = () => req(`${BASE}/genres`)
export const fetchKeywords = () => req(`${BASE}/keywords`)

export const createMovie = (body) => req(BASE, { method: 'POST', body: JSON.stringify(body) })
export const updateMovie = (id, body) => req(`${BASE}/${id}`, { method: 'PUT', body: JSON.stringify(body) })
export const deleteMovie = (id) => req(`${BASE}/${id}`, { method: 'DELETE' })
export const bulkDelete = (ids) => req(`${BASE}/bulk-delete`, { method: 'POST', body: JSON.stringify({ ids }) })
export const bulkEdit = (ids, patch) => req(`${BASE}/bulk-edit`, { method: 'POST', body: JSON.stringify({ ids, patch }) })
