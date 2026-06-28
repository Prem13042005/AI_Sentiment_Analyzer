import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getStats, getHistory } from '../services/api'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area
} from 'recharts'
import { 
  TrendingUp, 
  Database, 
  Smile, 
  Frown, 
  Cpu, 
  AlertCircle, 
  ChevronRight,
  RefreshCw
} from 'lucide-react'
import SentimentBadge from '../components/SentimentBadge'

const Dashboard = () => {
  const [stats, setStats] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const fetchDashboardData = async () => {
    setLoading(true)
    setError('')
    try {
      const [statsData, historyData] = await Promise.all([
        getStats(),
        getHistory({ limit: 10 })
      ])
      setStats(statsData)
      setHistory(historyData)
    } catch (err) {
      console.error(err)
      setError('Failed to fetch dashboard data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
  }, [])

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-teal border-t-transparent"></div>
          <span className="text-sm font-medium text-text-muted">Loading dashboard...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center max-w-lg mx-auto mt-12">
        <AlertCircle className="h-10 w-10 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-bold text-red-800">Connection Error</h3>
        <p className="text-sm text-red-600 mt-2">{error}</p>
        <button 
          onClick={fetchDashboardData}
          className="mt-6 inline-flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-semibold px-4 py-2 rounded-lg text-sm transition-all"
        >
          <RefreshCw className="h-4 w-4" /> Retry Connection
        </button>
      </div>
    )
  }

  // If total analyses is 0, show empty state
  const totalCount = stats?.total || 0
  const isEmpty = totalCount === 0

  if (isEmpty) {
    return (
      <div className="flex flex-col items-center justify-center py-20 px-6 bg-white border border-gray-border rounded-xl shadow-sm max-w-xl mx-auto text-center mt-12 gap-5">
        <div className="h-16 w-16 bg-teal/10 rounded-full flex items-center justify-center text-teal">
          <Database className="h-8 w-8" />
        </div>
        <h3 className="text-xl font-bold text-navy">No Analyses Recorded</h3>
        <p className="text-sm text-text-muted leading-relaxed max-w-md">
          To get started, submit customer reviews or comments on the Sentiment Analyzer page to generate metrics and insights.
        </p>
        <button 
          onClick={() => navigate('/analyzer')}
          className="bg-teal hover:bg-teal-dark text-white font-semibold px-6 py-3 rounded-lg text-sm shadow-md hover:shadow-teal/20 transition-all flex items-center gap-2 mt-2"
        >
          Go to Sentiment Analyzer &rarr;
        </button>
      </div>
    )
  }

  const positivePct = stats?.positive_pct || 0
  const negativePct = stats?.negative_pct || 0
  const topModel = stats?.most_used_model || 'None'

  // Prepare Sentiment Distribution Chart Data
  const distributionData = [
    { name: 'Positive', count: stats?.positive || 0, fill: '#22c55e' },
    { name: 'Neutral', count: stats?.neutral || 0, fill: '#94a3b8' },
    { name: 'Negative', count: stats?.negative || 0, fill: '#ef4444' }
  ]

  // Prepare 30 Days Activity Chart Data
  const activityData = (stats?.analyses_last_30_days || []).map(item => ({
    name: item.date.slice(5),
    count: item.count
  }))

  return (
    <div className="flex flex-col gap-8">
      
      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        
        {/* Total Analyses */}
        <div className="bg-white p-6 rounded-xl border border-gray-border shadow-sm flex items-center justify-between">
          <div className="flex flex-col gap-1">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">Total Analyses</span>
            <span className="text-2xl font-extrabold text-text-dark">{totalCount.toLocaleString()}</span>
          </div>
          <div className="h-12 w-12 rounded-lg bg-teal/10 text-teal flex items-center justify-center">
            <Database className="h-6 w-6" />
          </div>
        </div>

        {/* Positive Sentiment % (Average Score) */}
        <div className="bg-white p-6 rounded-xl border border-gray-border shadow-sm flex flex-col justify-between gap-3">
          <div className="flex items-center justify-between w-full">
            <div className="flex flex-col gap-1">
              <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">Average Score</span>
              <span className="text-2xl font-extrabold text-positive">{(stats?.positive_pct / 100 * 5).toFixed(1)}/5</span>
            </div>
            <div className="h-12 w-12 rounded-lg bg-emerald-50 text-positive flex items-center justify-center">
              <Smile className="h-6 w-6" />
            </div>
          </div>
          <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden mt-1">
            <div 
              className="bg-emerald-500 h-full rounded-full transition-all duration-500" 
              style={{ width: `${stats?.positive_pct || 0}%` }}
            ></div>
          </div>
        </div>

        {/* Negative Sentiment % */}
        <div className="bg-white p-6 rounded-xl border border-gray-border shadow-sm flex items-center justify-between">
          <div className="flex flex-col gap-1">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">Negative Ratio</span>
            <span className="text-2xl font-extrabold text-negative">{negativePct.toFixed(1)}%</span>
          </div>
          <div className="h-12 w-12 rounded-lg bg-red-50 text-negative flex items-center justify-center">
            <Frown className="h-6 w-6" />
          </div>
        </div>

        {/* Top Model Architecture */}
        <div className="bg-white p-6 rounded-xl border border-gray-border shadow-sm flex items-center justify-between">
          <div className="flex flex-col gap-1">
            <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">Top Architecture</span>
            <span className="text-lg font-extrabold text-navy truncate max-w-[130px] uppercase">{topModel}</span>
          </div>
          <div className="h-12 w-12 rounded-lg bg-blue-50 text-[#3b82f6] flex items-center justify-center">
            <Cpu className="h-6 w-6" />
          </div>
        </div>

      </div>

      {/* Chart Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Bar Chart: Distribution */}
        <div className="bg-white p-6 rounded-xl border border-gray-border shadow-sm">
          <h3 className="text-base font-bold text-text-dark mb-6">Sentiment Distribution Summary</h3>
          <div className="h-[260px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distributionData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis 
                  dataKey="name" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#8896ab', fontSize: 11 }}
                />
                <YAxis 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#8896ab', fontSize: 11 }}
                />
                <Tooltip 
                  cursor={{ fill: 'transparent' }}
                  contentStyle={{ background: '#0f1a2e', borderRadius: '8px', border: 'none', color: '#fff', fontSize: '12px' }}
                />
                <Bar 
                  dataKey="count" 
                  radius={[6, 6, 0, 0]} 
                  barSize={40}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Area/Line Chart: Activity */}
        <div className="bg-white p-6 rounded-xl border border-gray-border shadow-sm">
          <h3 className="text-base font-bold text-text-dark mb-6">Recent System Activity (Last 30 Days)</h3>
          <div className="h-[260px] w-full">
            {activityData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={activityData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="activity-gradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00b8a9" stopOpacity={0.2}/>
                      <stop offset="95%" stopColor="#00b8a9" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis 
                    dataKey="name" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#8896ab', fontSize: 11 }}
                  />
                  <YAxis 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#8896ab', fontSize: 11 }}
                    allowDecimals={false}
                  />
                  <Tooltip 
                    contentStyle={{ background: '#0f1a2e', borderRadius: '8px', border: 'none', color: '#fff', fontSize: '12px' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="count" 
                    stroke="#00b8a9" 
                    strokeWidth={2.5}
                    fillOpacity={1} 
                    fill="url(#activity-gradient)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-text-muted text-sm">
                No activity logs in the last 7 days.
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Recent Analyses List Table */}
      <div className="bg-white rounded-xl border border-gray-border shadow-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-border flex items-center justify-between">
          <h3 className="text-base font-bold text-text-dark">Recent Analyses</h3>
          {history.length > 0 && (
            <Link 
              to="/history" 
              className="text-teal font-semibold text-xs flex items-center gap-1 hover:underline"
            >
              View Full History <ChevronRight className="h-3 w-3" />
            </Link>
          )}
        </div>

        {history.length === 0 ? (
          <div className="p-8 text-center flex flex-col items-center">
            <span className="text-sm text-text-muted">No analyses yet. Go to the Analyzer to get started.</span>
            <button 
              onClick={() => navigate('/analyzer')}
              className="mt-4 bg-teal hover:bg-teal-dark text-white font-semibold px-5 py-2 rounded-lg text-sm shadow-md transition-all"
            >
              Run single analysis →
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-border text-[11px] font-bold text-text-muted uppercase tracking-wider">
                  <th className="px-6 py-4">Text Preview</th>
                  <th className="px-6 py-4">Sentiment Verdict</th>
                  <th className="px-6 py-4">Confidence</th>
                  <th className="px-6 py-4">Model Architecture</th>
                  <th className="px-6 py-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-border text-sm text-text-mid">
                {history.slice(0, 3).map((item) => {
                  const formattedDate = item.created_at 
                    ? new Date(item.created_at).toLocaleString('sv-SE', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit'
                      })
                    : 'N/A'
                  return (
                    <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 font-medium text-text-dark max-w-xs truncate" title={item.text_snippet}>
                        {item.text_snippet}
                      </td>
                      <td className="px-6 py-4">
                        <SentimentBadge sentiment={item.sentiment} />
                      </td>
                      <td className="px-6 py-4 font-semibold text-text-dark">
                        {(item.confidence * 100).toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 font-mono text-xs uppercase text-text-muted">
                        {item.model_used}
                      </td>
                      <td className="px-6 py-4 text-xs text-text-muted">
                        {formattedDate}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  )
}

export default Dashboard
