import MovieRow from './MovieRow'
import Pagination from './Pagination'
import { useSelection } from '../../store/selectionStore'

const COLUMNS = [
  { key: 'title', label: 'Title' },
  { key: 'year', label: 'Year' },
  { key: 'genre', label: 'Genre' },
  { key: 'director', label: 'Director' },
  { key: 'imdb_rating', label: 'IMDB' },
  { key: 'rt_score', label: 'RT' },
  { key: 'metascore', label: 'Meta' },
]

export default function MovieTable({ movies, total, page, totalPages, sort, dir, onSort, onPage, onEdit, onDelete }) {
  const { selected, selectAll, clear } = useSelection()
  const allChecked = movies.length > 0 && movies.every(m => selected.has(m.id))

  function toggleAll() {
    if (allChecked) clear()
    else selectAll(movies.map(m => m.id))
  }

  function SortTh({ col }) {
    const active = sort === col.key
    return (
      <th
        className="px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase cursor-pointer select-none hover:text-gray-800 whitespace-nowrap"
        onClick={() => onSort(col.key)}
      >
        {col.label}
        {active && <span className="ml-1">{dir === 'asc' ? '↑' : '↓'}</span>}
      </th>
    )
  }

  if (!movies.length) return (
    <div className="text-center py-16 text-gray-400">No movies found</div>
  )

  return (
    <div>
      <div className="text-xs text-gray-400 px-1 py-2">{total} movies</div>
      <div className="overflow-x-auto rounded-lg border">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-3 py-2">
                <input type="checkbox" checked={allChecked} onChange={toggleAll} className="cursor-pointer" />
              </th>
              <th className="px-3 py-2 w-10" />
              {COLUMNS.map(col => <SortTh key={col.key} col={col} />)}
              <th className="px-3 py-2" />
            </tr>
          </thead>
          <tbody>
            {movies.map(m => (
              <MovieRow key={m.id} movie={m} onEdit={onEdit} onDelete={onDelete} />
            ))}
          </tbody>
        </table>
      </div>
      <Pagination page={page} totalPages={totalPages} onPage={onPage} />
    </div>
  )
}
