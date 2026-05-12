import { useSelection } from '../../store/selectionStore'

export default function BulkBar({ onBulkDelete, onBulkEdit }) {
  const { selected, clear } = useSelection()
  if (selected.size === 0) return null

  return (
    <div className="sticky top-0 z-30 bg-blue-700 text-white px-4 py-2 flex items-center gap-4 shadow">
      <span className="text-sm font-medium">{selected.size} selected</span>
      <button onClick={onBulkEdit} className="text-sm bg-white/20 hover:bg-white/30 px-3 py-1 rounded">Edit</button>
      <button onClick={onBulkDelete} className="text-sm bg-red-500 hover:bg-red-600 px-3 py-1 rounded">Delete</button>
      <button onClick={clear} className="text-sm text-white/70 hover:text-white ml-auto">✕ Clear</button>
    </div>
  )
}
