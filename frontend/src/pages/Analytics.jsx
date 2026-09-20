import React, { useEffect, useState } from 'react'
import client from '../api/client'
import Loading from '../components/Loading'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function Analytics() {
  const [courses, setCourses] = useState([])
  const [enrollments, setEnrollments] = useState([])
  const [courseId, setCourseId] = useState('')
  const [data, setData] = useState(null)
  const [path, setPath] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    Promise.all([client.get('/api/courses'), client.get('/api/courses/mine/enrollments')])
      .then(([c, e]) => { setCourses(c.data); setEnrollments(e.data) })
  }, [])

  async function loadAnalytics(id) {
    setCourseId(id)
    if (!id) return
    setBusy(true)
    try {
      const [a, p] = await Promise.all([
        client.get(`/api/analytics/course/${id}`),
        client.get(`/api/analytics/course/${id}/learning-path`),
      ])
      setData(a.data)
      setPath(p.data.steps)
    } finally {
      setBusy(false)
    }
  }

  const myCourses = courses.filter(c => enrollments.some(e => e.course_id === c.id))

  return (
    <div>
      <p className="eyebrow mb-1">Module 7 & 8 · Explainable Learning Analytics</p>
      <h1 className="text-3xl font-semibold mb-6">My progress</h1>

      <div className="mb-6 max-w-sm">
        <label className="label">Course</label>
        <select className="input" value={courseId} onChange={e => loadAnalytics(e.target.value)}>
          <option value="">Select an enrolled course…</option>
          {myCourses.map(c => <option key={c.id} value={c.id}>{c.code} — {c.title}</option>)}
        </select>
      </div>

      {busy && <Loading />}

      {data && !busy && (
        <div className="space-y-6">
          <div className="grid sm:grid-cols-3 gap-4">
            <Stat label="Course completion" value={`${data.course_completion_percent}%`} />
            <Stat label="Predicted performance" value={`${data.predicted_performance}%`} />
            <Stat label="Prediction confidence" value={`${Math.round(data.confidence_score * 100)}%`} />
          </div>

          <div className="card">
            <h3 className="font-semibold mb-3">Topic mastery</h3>
            {data.topic_mastery.length === 0 ? (
              <p className="text-sm text-ink/50">No concepts defined for this course yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={data.topic_mastery}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#12172B10" />
                  <XAxis dataKey="concept" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="mastery_score" fill="#C98A3E" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="card">
            <h3 className="font-semibold mb-2">Why this prediction? (Explainable AI)</h3>
            <ul className="text-sm text-ink/70 space-y-1 list-disc list-inside">
              {data.recommendation_reasoning.map((r, i) => <li key={i}>{r}</li>)}
            </ul>
          </div>

          {data.weak_topics.length > 0 && (
            <div className="card">
              <h3 className="font-semibold mb-2">Weak areas identified</h3>
              <div className="flex flex-wrap gap-2">
                {data.weak_topics.map((t, i) => (
                  <span key={i} className="text-xs bg-red-50 text-red-700 rounded-full px-3 py-1">{t}</span>
                ))}
              </div>
            </div>
          )}

          {path && (
            <div className="card">
              <h3 className="font-semibold mb-3">Your personalized learning path</h3>
              <ol className="space-y-2">
                {path.map((s, i) => (
                  <li key={i} className="flex gap-3 items-start text-sm">
                    <span className="text-amber font-mono text-xs mt-0.5">{String(i + 1).padStart(2, '0')}</span>
                    <div>
                      <p className="font-medium">{s.concept} <span className="text-[10px] uppercase text-ink/40 ml-1">{s.type.replace('_', ' ')}</span></p>
                      <p className="text-ink/60">{s.reason}</p>
                    </div>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="card">
      <p className="text-xs uppercase tracking-wide text-ink/50">{label}</p>
      <p className="text-3xl font-semibold font-display mt-1">{value}</p>
    </div>
  )
}
