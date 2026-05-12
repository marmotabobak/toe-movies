export default function TagChip({ label, onRemove }) {
  return (
    <span className="inline-flex items-center gap-1 bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded-full">
      {label}
      {onRemove && (
        <button onClick={onRemove} className="hover:text-blue-500 leading-none">&times;</button>
      )}
    </span>
  )
}
