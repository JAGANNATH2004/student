import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'
import Loading from '../components/Loading'

export default function CourseList() {
  const { user } = useAuth()
  const [courses, setCourses] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ title: '', code: '', description: '' })
  const [error, setError] = useState('')

  async function load() {
    const { data } = await client.get('/api/courses')
    setCourses(data)
  }

  useEffect(() => { load() }, [])

  async function enroll(courseId) {
    await client.post(`/api/courses/${courseId}/enroll`)
    alert('Enrolled!')
  }

  async function createCourse(e) {
    e.preventDefault()
    setError('')
    try {
      await client.post('/api/courses', form)
      setForm({ title: '', code: '', description: '' })
      setShowForm(false)
      load()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Could not create course')
    }
  }

  if (!courses) return <Loading label="Loading courses…" />

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="eyebrow mb-1">Module 2</p>
          <h1 className="text-3xl font-semibold">Courses</h1>
        </div>
        {(user.role === 'faculty' || user.role === 'admin') && (
          <button className="btn-accent" onClick={() => setShowForm(s => !s)}>
            {showForm ? 'Cancel' : '+ New course'}
          </button>
        )}
      </div>

      {showForm && (
        <form onSubmit={createCourse} className="card mb-6 space-y-3">
          <div>
            <label className="label">Title</label>
            <input className="input" required value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
          </div>
          <div>
            <label className="label">Course code</label>
            <input className="input" required value={form.code} onChange={e => setForm(f => ({ ...f, code: e.target.value }))} />
          </div>
          <div>
            <label className="label">Description</label>
            <textarea className="input" rows={3} value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button className="btn-primary">Create course</button>
        </form>
      )}

      {courses.length === 0 ? (
        <p className="text-ink/50">No courses yet. {user.role === 'student' ? 'Check back soon.' : 'Create the first one above.'}</p>
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {courses.map((c) => (
            <div key={c.id} className="card flex flex-col">
              <span className="text-xs font-mono text-amber mb-1">{c.code}</span>
              <h3 className="font-semibold text-lg">{c.title}</h3>
              <p className="text-sm text-ink/60 mt-1 flex-1">{c.description || 'No description provided.'}</p>
              <div className="mt-4 flex gap-2">
                <Link to={`/courses/${c.id}`} className="btn-ghost !py-1.5 !px-3 text-sm">Open</Link>
                {user.role === 'student' && (
                  <button onClick={() => enroll(c.id)} className="btn-accent !py-1.5 !px-3 text-sm">Enroll</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
