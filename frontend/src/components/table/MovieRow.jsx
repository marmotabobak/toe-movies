import RatingBadge from '../common/RatingBadge'
import TagChip from '../common/TagChip'
import { useSelection } from '../../store/selectionStore'

export default function MovieRow({ movie, onEdit, onDelete }) {
  const { selected, toggle } = useSelection()
  const checked = selected.has(movie.id)

  return (
    <tr className={`border-b hover:bg-gray-50 ${checked ? 'bg-blue-50' : ''}`}>
      <td className="px-3 py-2">
        <input type="checkbox" checked={checked} onChange={() => toggle(movie.id)} className="cursor-pointer" />
      </td>
      <td className="px-3 py-2 w-10">
        {movie.poster_url
          ? <img src={movie.poster_url} alt="" className="w-8 h-12 object-cover rounded" loading="lazy" />
          : <div className="w-8 h-12 bg-gray-200 rounded" />}
      </td>
      <td className="px-3 py-2">
        <div className="font-medium text-sm text-gray-900">{movie.orig_name || movie.title}</div>
        {movie.orig_name && <div className="text-xs text-gray-400">{movie.title}</div>}
        {movie.keywords?.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {movie.keywords.slice(0, 4).map(kw => <TagChip key={kw} label={kw} />)}
          </div>
        )}
      </td>
      <td className="px-3 py-2 text-sm text-gray-600 whitespace-nowrap">{movie.year || '—'}</td>
      <td className="px-3 py-2 text-xs text-gray-500 max-w-[140px] truncate">{movie.genre || '—'}</td>
      <td className="px-3 py-2 text-xs text-gray-500 max-w-[120px] truncate">{movie.director || '—'}</td>
      <td className="px-3 py-2"><RatingBadge value={movie.imdb_rating} type="imdb" /></td>
      <td className="px-3 py-2"><RatingBadge value={movie.rt_score} type="rt" /></td>
      <td className="px-3 py-2 text-xs text-gray-500">{movie.metascore ?? '—'}</td>
      <td className="px-3 py-2 whitespace-nowrap">
        <button onClick={() => onEdit(movie.id)} className="text-xs text-blue-600 hover:underline mr-3">Edit</button>
        <button onClick={() => onDelete(movie.id)} className="text-xs text-red-500 hover:underline">Delete</button>
      </td>
    </tr>
  )
}
