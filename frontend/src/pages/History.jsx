import React, { useState, useEffect } from 'react'
import { getHistory, deleteHistoryItem } from '../services/api'
import SentimentBadge from '../components/SentimentBadge'
import SemiCircleGauge from '../components/SemiCircleGauge'
import { 
  Search, 
  Trash2, 
  Download, 
  Filter, 
  AlertCircle,
  Clock,
  ChevronLeft,
  ChevronRight,
  Loader2
} from 'lucide-react'

const History = () => {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState('')
  
  // Filters state
  const [search, setSearch] = useState('')
  const [sentimentFilter, setSentimentFilter] = useState('All')
  
  // Selection state
  const [selectedIds, setSelectedIds] = useState(new Set())

  const fetchHistoryLogs = async () => {
    setLoading(true)
    setError('')
    try {
      // Pull max 50 items as specified in specs
      const data = await getHistory({ limit: 50 })
      setHistory(data)
      setSelectedIds(new Set()) // clear selection
    } catch (err) {
      console.error(err)
      setError('Failed to retrieve history logs.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHistoryLogs()
  }, [])

  // Apply filters client-side
  const filteredLogs = history.filter(item => {
    const textMatch = item.text?.toLowerCase().includes(search.toLowerCase()) || 
                      item.text_snippet?.toLowerCase().includes(search.toLowerCase())
    
    const sentimentMatch = sentimentFilter === 'All' || 
                           item.sentiment?.toLowerCase() === sentimentFilter.toLowerCase()
    
    return textMatch && sentimentMatch
  })

  // Select / Deselect individual row
  const handleSelectRow = (id) => {
    const next = new Set(selectedIds)
    if (next.has(id)) {
      next.delete(id)
    } else {
      next.add(id)
    }
    setSelectedIds(next)
  }

  // Select / Deselect all visible filtered rows
  const handleSelectAll = () => {
    if (selectedIds.size === filteredLogs.length && filteredLogs.length > 0) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(filteredLogs.map(item => item.id)))
    }
  }

  // Handle bulk deletes
  const handleDeleteSelected = async () => {
    if (selectedIds.size === 0) return
    const confirm = window.confirm(`Are you sure you want to delete ${selectedIds.size} selected history record(s)?`)
    if (!confirm) return

    setDeleting(true)
    setError('')

    try {
      // Delete in parallel loop
      await Promise.all(
        Array.from(selectedIds).map(id => deleteHistoryItem(id))
      )
      await fetchHistoryLogs()
    } catch (err) {
      console.error(err)
      setError('An error occurred while deleting records. Some records might not have been removed.')
    } finally {
      setDeleting(false)
    }
  }

  // Handle individual row deletion
  const handleDeleteIndividual = async (id) => {
    const confirm = window.confirm('Are you sure you want to delete this analysis log?')
    if (!confirm) return

    try {
      await deleteHistoryItem(id)
      setHistory(prev => prev.filter(item => item.id !== id))
      setSelectedIds(prev => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    } catch (err) {
      console.error(err)
      setError('Failed to delete history record.')
    }
  }

  // Export visible filtered data to CSV
  const handleExportCSV = () => {
    if (filteredLogs.length === 0) return

    const headers = ['id', 'text', 'sentiment', 'confidence_pct', 'model_used', 'created_at']
    const csvContent = [
      headers.join(','),
      ...filteredLogs.map(item => {
        const textClean = (item.text || '').replace(/"/g, '""') // escape double quotes
        return [
          item.id,
          `"${textClean}"`,
          item.sentiment,
          (item.confidence * 100).toFixed(1),
          item.model_used,
          item.created_at
        ].join(',')
      })
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', `sentix_history_export_${Date.now()}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="flex flex-col gap-6">
      
      {/* Search & Filter Header Card */}
      <div className="bg-white p-5 rounded-xl border border-gray-border shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Left: Filter Controls */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 w-full md:w-auto">
          {/* Text Search */}
          <div className="relative min-w-[240px]">
            <input
              type="text"
              placeholder="Search content..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-border text-sm text-text-dark bg-gray-50 focus:bg-white focus:outline-none"
            />
            <Search className="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-text-muted" />
          </div>

          {/* Sentiment Dropdown */}
          <div className="relative">
            <select
              value={sentimentFilter}
              onChange={(e) => setSentimentFilter(e.target.value)}
              className="w-full pl-4 pr-10 py-2.5 rounded-lg border border-gray-border text-sm text-text-dark bg-gray-50 focus:bg-white focus:outline-none appearance-none font-medium"
            >
              <option value="All">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="negative">Negative</option>
              <option value="neutral">Neutral</option>
            </select>
            <Filter className="absolute right-3.5 top-3.5 h-4.5 w-4.5 text-text-muted pointer-events-none" />
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-3 w-full md:w-auto justify-end">
          <button
            onClick={handleExportCSV}
            disabled={filteredLogs.length === 0}
            className="flex items-center gap-2 bg-white border border-gray-border hover:bg-gray-50 text-text-dark font-semibold px-4 py-2.5 rounded-lg text-sm transition-all shadow-sm disabled:opacity-40"
          >
            <Download className="h-4 w-4" /> Export CSV
          </button>
        </div>

      </div>

      {/* Bulk Delete Floating Banner */}
      {selectedIds.size > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl px-6 py-4 flex items-center justify-between shadow-sm animate-pulse">
          <div className="flex items-center gap-2.5 text-red-800 text-sm font-semibold">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <span>Selected {selectedIds.size} log record(s) for deletion</span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSelectedIds(new Set())}
              className="text-text-muted hover:text-text-dark text-xs font-semibold"
              disabled={deleting}
            >
              Cancel
            </button>
            <button
              onClick={handleDeleteSelected}
              disabled={deleting}
              className="bg-red-600 hover:bg-red-700 text-white font-semibold px-4 py-2 rounded-lg text-xs flex items-center gap-1.5 shadow-sm transition-all"
            >
              {deleting ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" /> Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="h-3.5 w-3.5" /> Confirm Delete
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Main logs Table card */}
      <div className="bg-white rounded-xl border border-gray-border shadow-sm overflow-hidden min-h-[400px]">
        {loading ? (
          <div className="flex h-[350px] items-center justify-center">
            <div className="flex flex-col items-center gap-3">
              <div className="h-9 w-9 animate-spin rounded-full border-4 border-teal border-t-transparent"></div>
              <span className="text-sm font-medium text-text-muted">Loading logs archive...</span>
            </div>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-24 text-center px-4">
            <AlertCircle className="h-10 w-10 text-red-500 mb-3" />
            <h4 className="text-sm font-bold text-text-dark">Retrieval Failed</h4>
            <p className="text-xs text-text-muted mt-1">{error}</p>
          </div>
        ) : history.length === 0 ? (
          <div className="py-32 text-center flex flex-col items-center justify-center px-6">
            <Clock className="h-10 w-10 text-text-muted mb-4 opacity-50" />
            <span className="text-xs font-bold text-text-dark">No analyses completed</span>
            <p className="text-[11px] text-text-muted max-w-xs mt-1.5">
              Submit single reviews or bulk csv uploads to populate your system logs archive.
            </p>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="py-24 text-center flex flex-col items-center justify-center px-6">
            <Filter className="h-8 w-8 text-text-muted mb-4 opacity-50" />
            <span className="text-xs font-bold text-text-dark">No records matched</span>
            <p className="text-[11px] text-text-muted mt-1">
              Adjust your search keywords or sentiment filter category.
            </p>
          </div>
        ) : (
          <div className="flex flex-col h-full justify-between">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs md:text-sm">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-border text-[11px] font-bold text-text-muted uppercase tracking-wider select-none">
                    <th className="w-12 px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedIds.size === filteredLogs.length && filteredLogs.length > 0}
                        onChange={handleSelectAll}
                        className="rounded border-gray-300 text-teal focus:ring-teal cursor-pointer h-4 w-4"
                      />
                    </th>
                    <th className="px-6 py-4">Text Content</th>
                    <th className="px-6 py-4">Sentiment</th>
                    <th className="px-6 py-4">Confidence</th>
                    <th className="px-6 py-4">Model</th>
                    <th className="px-6 py-4">Date Added</th>
                    <th className="px-6 py-4 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-border text-xs md:text-sm text-text-mid">
                  {filteredLogs.map((item) => {
                    const isChecked = selectedIds.has(item.id)
                    const formattedDate = item.created_at
                      ? new Date(item.created_at).toLocaleString()
                      : 'N/A'
                    const textPreview = item.text_snippet && item.text_snippet.length > 60
                      ? item.text_snippet.slice(0, 60) + '...'
                      : item.text_snippet || ''
                    return (
                      <tr 
                        key={item.id} 
                        className={`hover:bg-gray-50 transition-colors ${isChecked ? 'bg-teal/5' : ''}`}
                      >
                        <td className="px-6 py-3.5">
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => handleSelectRow(item.id)}
                            className="rounded border-gray-300 text-teal focus:ring-teal cursor-pointer h-4 w-4"
                          />
                        </td>
                        <td 
                          className="px-6 py-3.5 font-medium text-text-dark max-w-sm truncate" 
                          title={item.text}
                        >
                          {textPreview}
                        </td>
                        <td className="px-6 py-3">
                          <SentimentBadge sentiment={item.sentiment} />
                        </td>
                        <td className="px-6 py-3.5 font-semibold text-text-dark">
                          {(item.confidence * 100).toFixed(1)}%
                        </td>
                        <td className="px-6 py-3.5 font-mono text-[11px] uppercase text-text-muted">
                          {item.model_used}
                        </td>
                        <td className="px-6 py-3.5 text-xs text-text-muted">
                          {formattedDate}
                        </td>
                        <td className="px-6 py-3.5 text-center">
                          <button
                            onClick={() => handleDeleteIndividual(item.id)}
                            className="p-1 text-text-muted hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                            title="Delete log"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            <div className="px-6 py-4 border-t border-gray-border bg-gray-50 flex items-center justify-between text-xs font-semibold text-text-muted">
              <span>Showing {filteredLogs.length} of {history.length} records</span>
              <span className="uppercase tracking-wider">Indexed Database logs</span>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Summary Gauge */}
      {filteredLogs.length > 0 && (
        <div className="bg-white p-6 rounded-xl border border-gray-border shadow-sm flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex flex-col gap-2">
            <h3 className="text-base font-bold text-navy">Filter Sentiment Summary</h3>
            <p className="text-xs text-text-muted leading-relaxed max-w-sm">
              Displays the calculated positive sentiment percentage for the current set of filtered system logs above.
            </p>
          </div>
          <div className="h-32 flex items-center justify-center">
            <SemiCircleGauge 
              value={Math.round(
                filteredLogs.length > 0 
                  ? (filteredLogs.filter(item => item.sentiment === 'positive').length / filteredLogs.length * 100)
                  : 0
              )} 
              label="Positive Ratio" 
              color="#22c55e" 
            />
          </div>
        </div>
      )}

    </div>
  )
}

export default History
