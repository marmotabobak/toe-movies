export default function RatingBadge({ value, type }) {
  if (value == null) return <span className="text-gray-400 text-xs">—</span>

  let color = 'bg-gray-200 text-gray-700'
  if (type === 'imdb') {
    if (value >= 8) color = 'bg-yellow-400 text-yellow-900'
    else if (value >= 6) color = 'bg-yellow-200 text-yellow-800'
    else color = 'bg-red-100 text-red-700'
  } else if (type === 'rt') {
    if (value >= 75) color = 'bg-green-500 text-white'
    else if (value >= 60) color = 'bg-green-200 text-green-800'
    else color = 'bg-red-100 text-red-700'
  }

  return (
    <span className={`inline-block px-1.5 py-0.5 rounded text-xs font-semibold ${color}`}>
      {type === 'imdb' ? value : `${value}%`}
    </span>
  )
}
