import React, { useState } from 'react'
import { predict } from '../services/api'
import SemiCircleGauge from '../components/SemiCircleGauge'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts'
import { 
  Search, 
  Info, 
  AlertTriangle, 
  Cpu, 
  CheckCircle2, 
  ChevronRight,
  TrendingUp
} from 'lucide-react'

const Analyzer = () => {
  const [text, setText] = useState('')
  const [modelName, setModelName] = useState('distilbert')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const charCount = text.length
  const isTooLong = charCount > 2000
  const isApproaching = charCount > 1900

  const handleAnalyze = async (e) => {
    e.preventDefault()
    if (!text.trim() || isTooLong) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const data = await predict(text.trim(), modelName)
      setResult(data)
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail || 'Prediction failed. Check your API server.')
    } finally {
      setLoading(false)
    }
  }

  // Model select options mapping
  const models = [
    { value: 'distilbert', label: 'DistilBERT' },
  ]

  // Color map helper
  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive': return '#22c55e'
      case 'negative': return '#ef4444'
      case 'neutral': return '#94a3b8'
      default: return '#94a3b8'
    }
  }

  // Pre-process model scores for Recharts
  const getModelScoresData = () => {
    if (!result?.model_scores) return []
    return result.model_scores.map(ms => ({
      name: ms.model_name.toUpperCase(),
      confidence: Math.round(ms.confidence * 100),
      sentiment: ms.sentiment,
      fill: getSentimentColor(ms.sentiment)
    }))
  }

  // Pre-process attention weights
  const getAttentionWeights = () => {
    if (!result?.attention_weights) return []
    return Object.entries(result.attention_weights)
      .map(([word, weight]) => ({ word, weight }))
      .sort((a, b) => b.weight - a.weight)
      .slice(0, 10)
  }

  // Highlight words according to LIME contributions
  const renderLimeText = () => {
    if (!result?.lime_words) return null
    return (
      <div className="flex flex-wrap gap-1 leading-loose text-sm border border-gray-border rounded-xl p-4 bg-gray-50">
        {result.lime_words.map((item, idx) => {
          const { word, weight } = item
          if (weight > 0.05) {
            return <span key={idx} className="lime-pos">{word}</span>
          } else if (weight < -0.05) {
            return <span key={idx} className="lime-neg">{word}</span>
          } else {
            return <span key={idx} className="text-text-mid px-1">{word}</span>
          }
        })}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      
      {/* Left Column: Input Form (Card) */}
      <div className="lg:col-span-6 bg-white p-6 md:p-8 rounded-xl border border-gray-border shadow-sm flex flex-col gap-6">
        <div>
          <h2 className="text-lg font-bold text-text-dark">Input Feedback</h2>
          <p className="text-xs text-text-muted mt-1">Submit customer reviews, feedback forms, or posts for NLP classification</p>
        </div>

        <form onSubmit={handleAnalyze} className="flex flex-col gap-5">
          {/* Text Area */}
          <div className="flex flex-col gap-1.5">
            <label htmlFor="feedback-text" className="text-xs font-bold text-text-dark uppercase tracking-wider">
              Enter text to analyze
            </label>
            <textarea
              id="feedback-text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste a review, comment, or any text here..."
              className="w-full h-44 rounded-lg border border-gray-border p-4 text-sm text-text-dark bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal/30 focus:border-teal transition-all resize-none"
              maxLength={2200}
            />
            {/* Character Count indicators */}
            <div className="flex justify-between items-center mt-1">
              <span className={`text-[11px] font-semibold ${isTooLong ? 'text-red-500' : 'text-text-muted'}`}>
                {charCount} / 2000 characters
              </span>
              {isApproaching && !isTooLong && (
                <span className="text-[11px] font-bold text-warning flex items-center gap-1">
                  <AlertTriangle className="h-3.5 w-3.5" /> Approaching character limit
                </span>
              )}
              {isTooLong && (
                <span className="text-[11px] font-bold text-red-500 flex items-center gap-1">
                  <AlertTriangle className="h-3.5 w-3.5" /> Exceeds 2000 char limit
                </span>
              )}
            </div>
          </div>



          {/* Action Trigger */}
          <button
            type="submit"
            disabled={loading || !text.trim() || isTooLong}
            className="w-full mt-2 bg-teal hover:bg-teal-dark text-white font-semibold py-3.5 rounded-lg shadow-md hover:shadow-teal/20 transition-all flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                Analyzing feedback...
              </>
            ) : (
              <>
                <Search className="h-4 w-4" /> Analyze Sentiment
              </>
            )}
          </button>
        </form>
      </div>

      {/* Right Column: Prediction Output (Card) */}
      <div className="lg:col-span-6 bg-white p-6 md:p-8 rounded-xl border border-gray-border shadow-sm min-h-[460px] flex flex-col justify-center gap-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-teal border-t-transparent"></div>
            <span className="text-sm font-semibold text-text-muted animate-pulse">Running neural network inference...</span>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center text-center py-16 px-4">
            <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center text-red-500 mb-4">
              <AlertTriangle className="h-6 w-6" />
            </div>
            <h3 className="text-base font-bold text-text-dark">Prediction Service Failed</h3>
            <p className="text-xs text-text-muted mt-2 max-w-sm leading-relaxed">{error}</p>
          </div>
        ) : result ? (
          <div className="flex flex-col gap-6">
            <div>
              <h2 className="text-lg font-bold text-text-dark">Analysis Output</h2>
              <p className="text-xs text-text-muted mt-1">Processed in {Math.round(result.processing_time_ms)}ms using {result.model_used.toUpperCase()}</p>
            </div>

            {/* Gauge Representation */}
            <div className="flex flex-col items-center justify-center border-b border-gray-border pb-6 mt-4 gap-4">
              <SemiCircleGauge 
                value={Math.round(result.confidence * 100)} 
                label={result.sentiment} 
                color={getSentimentColor(result.sentiment)} 
              />
              <p className="text-xs text-center text-text-mid font-medium max-w-md mt-2 leading-relaxed">
                DistilBERT analyzed your text and detected <strong className="capitalize" style={{ color: getSentimentColor(result.sentiment) }}>{result.sentiment}</strong> sentiment with <strong>{Math.round(result.confidence * 100)}%</strong> confidence in <strong>{Math.round(result.processing_time_ms)}</strong>ms.
              </p>
            </div>

            {/* Model Breakdown Chart (if Ensemble) */}
            {result.model_scores && result.model_scores.length > 1 && (
              <div className="flex flex-col gap-3">
                <h3 className="text-xs font-bold text-text-dark uppercase tracking-wider flex items-center gap-1.5">
                  <Cpu className="h-4 w-4 text-text-muted" /> Model Ensemble Breakdown
                </h3>
                <div className="h-[180px] w-full border border-gray-border rounded-xl p-3 bg-gray-50">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={getModelScoresData()}
                      layout="vertical"
                      margin={{ top: 5, right: 10, left: 10, bottom: 5 }}
                    >
                      <XAxis type="number" domain={[0, 100]} hide />
                      <YAxis 
                        dataKey="name" 
                        type="category" 
                        axisLine={false} 
                        tickLine={false} 
                        tick={{ fill: '#4a5568', fontSize: 10, fontWeight: 500 }}
                        width={75}
                      />
                      <Tooltip 
                        formatter={(value, name, props) => [`${value}% (${props.payload.sentiment})`, 'Confidence']}
                        contentStyle={{ background: '#0f1a2e', borderRadius: '8px', border: 'none', color: '#fff', fontSize: '11px' }}
                      />
                      <Bar dataKey="confidence" radius={[0, 4, 4, 0]} barSize={12}>
                        {getModelScoresData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* LIME highlights */}
            {result.lime_words && result.lime_words.length > 0 && (
              <div className="flex flex-col gap-3">
                <h3 className="text-xs font-bold text-text-dark uppercase tracking-wider flex items-center gap-1.5">
                  <Info className="h-4 w-4 text-text-muted" /> Word Attribution (LIME)
                </h3>
                {renderLimeText()}
                <span className="text-[10px] text-text-muted font-semibold uppercase">
                  Green = contributes to positive · Red = contributes to negative
                </span>
              </div>
            )}

            {/* GRU Attention mapping */}
            {result.attention_weights && Object.keys(result.attention_weights).length > 0 && (
              <div className="flex flex-col gap-3">
                <h3 className="text-xs font-bold text-text-dark uppercase tracking-wider flex items-center gap-1.5">
                  <TrendingUp className="h-4 w-4 text-text-muted" /> Attention weights (GRU)
                </h3>
                <div className="overflow-hidden border border-gray-border rounded-xl">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-gray-50 border-b border-gray-border text-[10px] font-bold text-text-muted uppercase">
                        <th className="px-4 py-2">Word</th>
                        <th className="px-4 py-2 text-right">Attention</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-border text-text-mid font-medium">
                      {getAttentionWeights().map((item, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-4 py-2 font-semibold text-text-dark">{item.word}</td>
                          <td className="px-4 py-2 text-right font-mono text-text-muted">{(item.weight).toFixed(4)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

          </div>
        ) : (
          <div className="flex flex-col items-center justify-center text-center py-20 px-6">
            <div className="h-14 w-14 rounded-2xl bg-teal/5 text-teal border border-teal/10 flex items-center justify-center mb-5 animate-pulse">
              <Search className="h-6 w-6" />
            </div>
            <h3 className="text-base font-bold text-text-dark">Analysis Report</h3>
            <p className="text-xs text-text-muted mt-2 max-w-xs leading-relaxed">
              Input reviews in the form on the left and trigger prediction to view detailed probability scores and explanations.
            </p>
          </div>
        )}
      </div>

    </div>
  )
}

export default Analyzer
