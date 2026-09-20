import React, { useEffect, useState } from 'react'
import client from '../api/client'
import Loading from '../components/Loading'

export default function AdminDashboard() {
  const [data, setData] = useState(null)

  useEffect(() => {
    client.get('/api/admin/overview').then(r => setData(r.data))
  }, [])

  if (!data) return <Loading />

  return (
    <div>
      <p className="eyebrow mb-1">Module 9 · Analytics Dashboard</p>
      <h1 className="text-3xl font-semibold mb-6">Platform overview</h1>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Stat label="Students" value={data.total_students} />
        <Stat label="Courses" value={data.total_courses} />
        <Stat label="Materials" value={data.total_materials} />
        <Stat label="Avg. quiz score" value={`${data.average_quiz_score}%`} />
      </div>

      <div className="card">
        <h3 className="font-semibold mb-3">Course engagement</h3>
        {data.course_engagement.length === 0 ? (
          <p className="text-sm text-ink/50">No courses yet.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-ink/50 border-b border-ink/10">
                <th className="py-2">Course</th>
                <th className="py-2">Enrollments</th>
              </tr>
            </thead>
            <tbody>
              {data.course_engagement.map(c => (
                <tr key={c.course_id} className="border-b border-ink/5">
                  <td className="py-2">{c.title}</td>
                  <td className="py-2">{c.enrollment_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
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
