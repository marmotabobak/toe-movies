import { useState, useEffect } from 'react'
import TagChip from '../common/TagChip'
import { fetchKeywords } from '../../api/movies'

export default function KeywordsField({ value = [], onChange }) {
  const [input, setInput] = useState('')
  const [allKeywords, setAllKeywords] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)

  useEffect(() => {
    fetchKeywords().then(data => setAllKeywords(data.keywords)).catch(() => {})
  }, [])

  const suggestions = input.trim()
    ? allKeywords.filter(k => k.includes(input.trim().toLowerCase()) && !value.includes(k))
    : []

  function add(kw = input) {
    const k = kw.trim().toLowerCase()
    if (k && !value.includes(k)) onChange([...value, k])
    setInput('')
    setShowSuggestions(false)
  }

  function remove(kw) {
    onChange(value.filter(k => k !== kw))
  }

  return (
    <div className="relative">
      <div className="flex flex-wrap gap-1 mb-2 min-h-[28px]">
        {value.map(kw => <TagChip key={kw} label={kw} onRemove={() => remove(kw)} />)}
      </div>
      <input
        className="border rounded px-2 py-1 text-sm w-full"
        placeholder="Type keyword, press Enter"
        value={input}
        onChange={e => { setInput(e.target.value); setShowSuggestions(true) }}
        onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); add() } }}
        onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
        onFocus={() => setShowSuggestions(true)}
      />
      {showSuggestions && suggestions.length > 0 && (
        <ul className="absolute z-10 left-0 right-0 bg-white border rounded shadow-md max-h-48 overflow-y-auto text-sm mt-1">
          {suggestions.map(k => (
            <li
              key={k}
              className="px-3 py-1.5 hover:bg-blue-50 cursor-pointer"
              onMouseDown={() => add(k)}
            >
              {k}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
