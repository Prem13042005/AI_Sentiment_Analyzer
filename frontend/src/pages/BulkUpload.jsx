import React, { useState, useRef, useEffect } from 'react'
import Papa from 'papaparse'
import { predictBulk, getHistory } from '../services/api'
import SentimentBadge from '../components/SentimentBadge'
import { 
  UploadCloud, 
  FileSpreadsheet, 
  AlertTriangle, 
  CheckCircle2, 
  Download, 
  Play,
  X
} from 'lucide-react'

const BulkUpload = () => {
  const [file, setFile] = useState(null)
  const [csvData, setCsvData] = useState(null) // { headers, rows }
  const [textColumn, setTextColumn] = useState('')
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState(null) // Array of predictions combined with CSV rows
  const [recentUploads, setRecentUploads] = useState([])
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)

  const fetchRecentUploads = async () => {
    try {
      const data = await getHistory({ limit: 100 })
      const bulkLogs = data.filter(item => item.source === 'bulk')
      setRecentUploads(bulkLogs.slice(0, 10))
    } catch (err) {
      console.error('Failed to load recent bulk uploads:', err)
    }
  }

  useEffect(() => {
    fetchRecentUploads()
  }, [results])

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.name.endsWith('.csv')) {
      processFile(droppedFile)
    } else {
      setError('Invalid file type. Please upload a CSV file.')
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      processFile(selectedFile)
    }
  }

  const processFile = (selectedFile) => {
    setError('')
    setResults(null)
    setCsvData(null)
    setFile(selectedFile)

    Papa.parse(selectedFile, {
      header: true,
      skipEmptyLines: true,
      complete: (output) => {
        const headers = output.meta.fields || []
        const rows = output.data
        
        if (rows.length === 0) {
          setError('CSV file is empty.')
          setFile(null)
          return
        }
        
        if (rows.length > 100) {
          setError('Max 100 rows supported. Please trim your CSV.')
          setFile(null)
          return
        }

        setCsvData({ headers, rows })
        if (headers.length > 0) {
          setTextColumn(headers[0])
        }
      },
      error: (err) => {
        setError('Failed to parse CSV file: ' + err.message)
        setFile(null)
      }
    })
  }

  const handleAnalyze = async () => {
    if (!csvData || !textColumn) return
    setLoading(true)
    setError('')
    setProgress(10)

    const texts = csvData.rows.map(row => (row[textColumn] || '').slice(0, 2000))
    
    // Animate fake progress to mimic server operations
    const progressInterval = setInterval(() => {
      setProgress(prev => (prev < 90 ? prev + 15 : prev))
    }, 300)

    try {
      // Trigger bulk prediction in single HTTP request
      const response = await predictBulk(texts)
      
      setProgress(100)
      clearInterval(progressInterval)

      // Merge API response back into CSV rows
      const apiResults = response.results
      const combinedRows = csvData.rows.map((row, idx) => ({
        ...row,
        sentiment: apiResults[idx]?.sentiment || 'neutral',
        confidence: apiResults[idx]?.confidence || 0.0
      }))

      setResults({
        headers: [...csvData.headers, 'sentiment', 'confidence_pct'],
        rows: combinedRows
      })
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail || 'Bulk processing failed. Verify server status.')
    } finally {
      clearInterval(progressInterval)
      setLoading(false)
    }
  }

  const handleDownload = () => {
    if (!results) return

    // Convert results rows back to CSV string
    const csvContent = [
      results.headers.join(','),
      ...results.rows.map(row => 
        results.headers.map(header => {
          let value = row[header]
          if (header === 'confidence_pct') {
            value = (row.confidence * 100).toFixed(1)
          }
          // Wrap values containing commas in quotes to prevent structural break
          const strValue = String(value)
          return strValue.includes(',') ? `"${strValue}"` : strValue
        }).join(',')
      )
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', `sentix_bulk_results_${Date.now()}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleClear = () => {
    setFile(null)
    setCsvData(null)
    setTextColumn('')
    setResults(null)
    setError('')
  }

  return (
    <div className="flex flex-col gap-8">
      
      {/* Description Header */}
      <div className="bg-white border border-gray-border rounded-xl p-5 shadow-sm">
        <h2 className="text-base font-bold text-text-dark">Bulk CSV Analysis Sandbox</h2>
        <p className="text-xs text-text-muted mt-1 leading-relaxed">
          Upload structured spreadsheets containing feedback reviews. Max 100 rows supported. Our parallel pipelines will process and merge predictions back into your template.
        </p>
      </div>

      {/* Main interface cards */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Upload Column */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          
          {/* File input drag drop block */}
          <div className="bg-white p-6 rounded-xl border border-gray-border shadow-sm flex flex-col gap-4">
            <h3 className="text-sm font-bold text-text-dark">Upload Feed File</h3>
            
            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-xs font-semibold text-red-600 flex items-start gap-2">
                <AlertTriangle className="h-4 w-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {!file ? (
              <div
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-text-muted/30 rounded-xl p-8 flex flex-col items-center justify-center gap-3 cursor-pointer hover:border-teal hover:bg-teal/5 transition-all text-center"
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept=".csv"
                  className="hidden"
                />
                <UploadCloud className="h-10 w-10 text-text-muted" />
                <div>
                  <span className="text-xs font-bold text-teal">Click to upload</span>
                  <span className="text-xs text-text-muted"> or drag & drop</span>
                </div>
                <span className="text-[10px] text-text-muted uppercase font-semibold">CSV file up to 100 rows</span>
              </div>
            ) : (
              <div className="border border-gray-border rounded-xl p-4 flex items-center justify-between bg-gray-50">
                <div className="flex items-center gap-3 overflow-hidden">
                  <FileSpreadsheet className="h-8 w-8 text-teal flex-shrink-0" />
                  <div className="flex flex-col overflow-hidden">
                    <span className="text-xs font-bold text-text-dark truncate">{file.name}</span>
                    <span className="text-[10px] text-text-muted font-medium">
                      {(file.size / 1024).toFixed(1)} KB · {csvData?.rows?.length} rows
                    </span>
                  </div>
                </div>
                <button 
                  onClick={handleClear}
                  className="p-1 rounded-full hover:bg-gray-200 text-text-muted hover:text-text-dark"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}

            {/* Column Selector & Action Button */}
            {csvData && !results && (
              <div className="flex flex-col gap-4 mt-2">
                <div className="flex flex-col gap-1.5">
                  <label htmlFor="col-select" className="text-xs font-bold text-text-dark uppercase tracking-wider">
                    Text Content Column
                  </label>
                  <select
                    id="col-select"
                    value={textColumn}
                    onChange={(e) => setTextColumn(e.target.value)}
                    className="w-full rounded-lg border border-gray-border px-3 py-2 text-xs text-text-dark bg-gray-50 focus:bg-white focus:outline-none"
                  >
                    {csvData.headers.map(h => (
                      <option key={h} value={h}>{h}</option>
                    ))}
                  </select>
                </div>

                <button
                  onClick={handleAnalyze}
                  disabled={loading}
                  className="w-full bg-teal hover:bg-teal-dark text-white font-semibold py-3 rounded-lg shadow-sm transition-all flex items-center justify-center gap-2 text-xs disabled:opacity-50"
                >
                  <Play className="h-3.5 w-3.5" /> Run Batch Inference
                </button>
              </div>
            )}
          </div>

          {/* Recent Bulk Uploads Panel */}
          <div className="bg-white p-6 rounded-xl border border-gray-border shadow-sm flex flex-col gap-4 mt-6">
            <h3 className="text-sm font-bold text-text-dark">Recent Bulk Uploads</h3>
            {recentUploads.length === 0 ? (
              <span className="text-xs text-text-muted">No recent bulk uploads.</span>
            ) : (
              <div className="flex flex-col gap-2 max-h-[250px] overflow-y-auto pr-1">
                {recentUploads.map((item) => (
                  <div key={item.id} className="border border-gray-border rounded-lg p-2.5 bg-gray-50 flex items-center justify-between text-xs hover:bg-gray-100/70 transition-colors">
                    <div className="flex flex-col gap-1 overflow-hidden max-w-[140px]">
                      <span className="font-medium text-text-dark truncate" title={item.text_snippet}>{item.text_snippet}</span>
                      <span className="text-[10px] text-text-muted">{new Date(item.created_at).toLocaleDateString()}</span>
                    </div>
                    <SentimentBadge sentiment={item.sentiment} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Preview / Results Column */}
        <div className="lg:col-span-8">
          
          {/* Progress Indicators */}
          {loading && (
            <div className="bg-white p-6 rounded-xl border border-gray-border shadow-sm mb-6 flex flex-col gap-3">
              <div className="flex justify-between items-center text-xs font-semibold">
                <span className="text-text-dark">Processing CSV payload...</span>
                <span className="text-teal">{progress}%</span>
              </div>
              <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                <div 
                  className="bg-teal h-full rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Table display */}
          <div className="bg-white rounded-xl border border-gray-border shadow-sm overflow-hidden min-h-[300px]">
            
            {/* Headers action section */}
            <div className="px-6 py-5 border-b border-gray-border flex items-center justify-between">
              <h3 className="text-sm font-bold text-text-dark">
                {results ? 'Analysis Results' : csvData ? 'CSV File Preview (First 5 Rows)' : 'Spreadsheet Viewer'}
              </h3>

              {results && (
                <button
                  onClick={handleDownload}
                  className="bg-teal hover:bg-teal-dark text-white font-semibold px-4 py-2 rounded-lg text-xs flex items-center gap-1.5 shadow-sm transition-all"
                >
                  <Download className="h-3.5 w-3.5" /> Export Results
                </button>
              )}
            </div>

            {/* Empty state */}
            {!csvData && !results && (
              <div className="py-24 text-center flex flex-col items-center justify-center px-6">
                <FileSpreadsheet className="h-10 w-10 text-text-muted mb-4 opacity-50" />
                <span className="text-xs text-text-muted">No spreadsheet uploaded yet</span>
                <span className="text-[10px] text-text-muted/70 mt-1 max-w-xs leading-relaxed">
                  Upload a comma-separated value file to inspect preview and map attributes.
                </span>
              </div>
            )}

            {/* File preview view (when csv uploaded but not processed) */}
            {csvData && !results && (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-border text-[10px] font-bold text-text-muted uppercase tracking-wider">
                      {csvData.headers.map((h, i) => (
                        <th key={i} className="px-5 py-3.5">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-border text-text-mid">
                    {csvData.rows.slice(0, 5).map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-gray-50/50">
                        {csvData.headers.map((h, cIdx) => (
                          <td key={cIdx} className="px-5 py-3 max-w-[180px] truncate">{row[h]}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Results table (after process execution) */}
            {results && (
              <div className="flex flex-col">
                <div className="bg-emerald-50 border-b border-emerald-100 p-4 text-xs font-semibold text-emerald-800 flex items-center gap-2">
                  <CheckCircle2 className="h-4.5 w-4.5 text-emerald-600 flex-shrink-0" />
                  <span>Success! Completed batch classification on {results.rows.length} records.</span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="bg-gray-50 border-b border-gray-border text-[10px] font-bold text-text-muted uppercase tracking-wider">
                        {csvData.headers.map((h, i) => (
                          <th key={i} className="px-5 py-3.5">{h}</th>
                        ))}
                        <th className="px-5 py-3.5">Sentiment</th>
                        <th className="px-5 py-3.5">Confidence</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-border text-text-mid">
                      {results.rows.map((row, rIdx) => (
                        <tr key={rIdx} className="hover:bg-gray-50">
                          {csvData.headers.map((h, cIdx) => (
                            <td key={cIdx} className="px-5 py-3 max-w-[180px] truncate">{row[h]}</td>
                          ))}
                          <td className="px-5 py-2.5">
                            <SentimentBadge sentiment={row.sentiment} />
                          </td>
                          <td className="px-5 py-3 font-semibold text-text-dark">
                            {(row.confidence * 100).toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

          </div>
        </div>

      </div>

    </div>
  )
}

export default BulkUpload
