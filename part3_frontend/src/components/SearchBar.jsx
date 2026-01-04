import { useState } from 'react'

export default function SearchBar({ onSearch, onResultClick }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [searching, setSearching] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setSearching(true)
    try {
      const searchResults = await onSearch(query)
      setResults(searchResults || [])
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="search-bar">
      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '8px' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search conversation..."
          style={{
            flex: 1,
            padding: '8px 12px',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        />
        <button
          type="submit"
          disabled={searching}
          style={{
            padding: '8px 16px',
            background: '#4a90d9',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {searching ? '...' : '🔍'}
        </button>
      </form>

      {results.length > 0 && (
        <div className="search-results" style={{
          marginTop: '10px',
          border: '1px solid #ddd',
          borderRadius: '4px',
          maxHeight: '200px',
          overflow: 'auto'
        }}>
          {results.map((result, i) => (
            <div
              key={i}
              onClick={() => onResultClick?.(result.message_index)}
              style={{
                padding: '10px',
                borderBottom: '1px solid #eee',
                cursor: 'pointer',
                background: i % 2 ? '#f9f9f9' : 'white'
              }}
            >
              <span style={{
                display: 'inline-block',
                padding: '2px 6px',
                background: result.role === 'user' ? '#e3f2fd' : '#f5f5f5',
                borderRadius: '4px',
                fontSize: '12px',
                marginRight: '8px'
              }}>
                {result.role}
              </span>
              <span style={{ fontSize: '14px' }}>{result.snippet}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
