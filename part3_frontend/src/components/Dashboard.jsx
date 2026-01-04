import { useState, useEffect } from 'react'

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null)
  const [dailyUsage, setDailyUsage] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      const [metricsRes, dailyRes] = await Promise.all([
        fetch('/api/analytics/usage'),
        fetch('/api/analytics/daily')
      ])
      setMetrics(await metricsRes.json())
      setDailyUsage(await dailyRes.json())
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div style={{ padding: '20px' }}>Loading analytics...</div>

  return (
    <div className="dashboard" style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '20px' }}>Analytics Dashboard</h1>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <MetricCard title="Total Sessions" value={metrics?.total_sessions || 0} />
        <MetricCard title="Total Messages" value={metrics?.total_messages || 0} />
        <MetricCard title="Total Cost" value={`$${(metrics?.total_cost || 0).toFixed(4)}`} />
        <MetricCard title="Cache Savings" value={`$${(metrics?.total_savings || 0).toFixed(4)}`} color="#10b981" />
        <MetricCard title="Cache Hit Rate" value={`${((metrics?.cache_hit_rate || 0) * 100).toFixed(1)}%`} />
        <MetricCard title="Avg Response" value={`${(metrics?.avg_response_time || 0).toFixed(2)}s`} />
      </div>

      <h2 style={{ marginBottom: '15px' }}>Daily Usage (Last 30 Days)</h2>
      <div style={{ overflowX: 'auto' }}>
        <div style={{ display: 'flex', gap: '4px', minWidth: '600px', alignItems: 'flex-end', height: '150px' }}>
          {dailyUsage.slice(-30).map((day, i) => (
            <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div style={{
                width: '100%',
                height: `${Math.max(4, (day.messages / Math.max(...dailyUsage.map(d => d.messages || 1))) * 120)}px`,
                background: '#4a90d9',
                borderRadius: '2px 2px 0 0'
              }} title={`${day.messages} messages`} />
              <span style={{ fontSize: '10px', marginTop: '4px' }}>{day.date.slice(-2)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function MetricCard({ title, value, color = '#1f2937' }) {
  return (
    <div style={{
      background: 'white',
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '20px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>{title}</div>
      <div style={{ fontSize: '24px', fontWeight: 'bold', color }}>{value}</div>
    </div>
  )
}
