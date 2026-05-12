import { useState } from 'react'
import { SelectionProvider, useSelection } from './store/selectionStore'
import { useMovies } from './hooks/useMovies'
import { deleteMovie, bulkDelete } from './api/movies'
import FilterBar from './components/filters/FilterBar'
import MovieTable from './components/table/MovieTable'
import BulkBar from './components/table/BulkBar'
import MovieModal from './components/modals/MovieModal'
import BulkEditModal from './components/modals/BulkEditModal'
import ConfirmDialog from './components/common/ConfirmDialog'
import Spinner from './components/common/Spinner'

function Main() {
  const [filters, setFilters] = useState({ sort: 'title', dir: 'asc', page: 1, limit: 50 })
  const [refetchKey, setRefetchKey] = useState(0)
  const [modal, setModal] = useState(null) // null | 'add' | number (movieId)
  const [deleteTarget, setDeleteTarget] = useState(null) // null | number | 'bulk'
  const [bulkEditOpen, setBulkEditOpen] = useState(false)
  const { selected, clear } = useSelection()

  const { movies, total, totalPages, loading, error } = useMovies(filters, refetchKey)

  function changeFilters(patch) {
    setFilters(f => ({ ...f, ...patch, page: 'page' in patch ? patch.page : 1 }))
    clear()
  }

  function onSort(col) {
    setFilters(f => ({
      ...f,
      sort: col,
      dir: f.sort === col && f.dir === 'asc' ? 'desc' : 'asc',
      page: 1,
    }))
  }

  function refetch() {
    setRefetchKey(k => k + 1)
    clear()
  }

  async function confirmDelete() {
    if (deleteTarget === 'bulk') {
      await bulkDelete([...selected])
    } else {
      await deleteMovie(deleteTarget)
    }
    setDeleteTarget(null)
    refetch()
  }

  const deleteMessage = deleteTarget === 'bulk'
    ? `Delete ${selected.size} selected movies?`
    : 'Delete this movie?'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Nav */}
      <header className="bg-white border-b px-6 py-3 flex items-center justify-between shadow-sm">
        <h1 className="text-lg font-bold text-gray-900">tvoe-movies</h1>
        <button
          onClick={() => setModal('add')}
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm px-4 py-2 rounded-lg"
        >
          + Add Movie
        </button>
      </header>

      <BulkBar
        onBulkDelete={() => setDeleteTarget('bulk')}
        onBulkEdit={() => setBulkEditOpen(true)}
      />

      <FilterBar filters={filters} onChange={changeFilters} />

      <main className="px-4 py-4">
        {error && <div className="text-red-500 text-sm mb-4">Error: {error}</div>}
        {loading ? <Spinner /> : (
          <MovieTable
            movies={movies}
            total={total}
            page={filters.page}
            totalPages={totalPages}
            sort={filters.sort}
            dir={filters.dir}
            onSort={onSort}
            onPage={p => changeFilters({ page: p })}
            onEdit={id => setModal(id)}
            onDelete={id => setDeleteTarget(id)}
          />
        )}
      </main>

      {modal != null && (
        <MovieModal
          movieId={modal === 'add' ? null : modal}
          onClose={() => setModal(null)}
          onSaved={() => { setModal(null); refetch() }}
        />
      )}

      {deleteTarget != null && (
        <ConfirmDialog
          message={deleteMessage}
          onConfirm={confirmDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}

      {bulkEditOpen && (
        <BulkEditModal
          ids={[...selected]}
          onClose={() => setBulkEditOpen(false)}
          onSaved={() => { setBulkEditOpen(false); refetch() }}
        />
      )}
    </div>
  )
}

export default function App() {
  return (
    <SelectionProvider>
      <Main />
    </SelectionProvider>
  )
}
