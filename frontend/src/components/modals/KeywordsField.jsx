import { useState } from 'react'
import TagChip from '../common/TagChip'

export default function KeywordsField({ value = [], onChange }) {
  const [input, setInput] = useState('')

  function add() {
    const kw = input.trim().toLowerCase()
    if (kw && !value.includes(kw)) {
      onChange([...value, kw])
    }
    setInput('')
  }

  function remove(kw) {
    onChange(value.filter(k => k !== kw))
  }

  return (
    <div>
      <div className="flex flex-wrap gap-1 mb-2 min-h-[28px]">
        {value.map(kw => <TagChip key={kw} label={kw} onRemove={() => remove(kw)} />)}
      </div>
      <input
        className="border rounded px-2 py-1 text-sm w-full"
        placeholder="Type keyword, press Enter"
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); add() } }}
      />
    </div>
  )
}
