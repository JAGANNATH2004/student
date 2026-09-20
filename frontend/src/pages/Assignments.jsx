import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import client from '../api/client'
import Loading from '../components/Loading'
import { useAuth } from '../context/AuthContext'

export default function Assignments() {
  const { courseId } = useParams()
  const { user } = useAuth()
  const [assignments, setAssignments] = useState(null)
  const [form, setForm] = useState({ title: '', instructions: '' })
  const [answerDrafts, setAnswerDrafts] = useState({})
  const [feedback, setFeedback] = useState({})

  async function load() {
    const { data } = await client.get(`/api/assignments/course/${courseId}`)
    setAssignments(data)
  }
  useEffect(() => { load() }, [courseId])

  async function createAssignment(e) {
    e.preventDefault()
    await client.post('/api/assignments', { course_id: Number(courseId), ...form })
    setForm({ title: '', instructions: '' })
    load()
  }

  async function submit(assignmentId) {
    const text = answerDrafts[assignmentId]
    if (!text?.trim()) return
    const { data } = await client.post('/api/assignments/submit', {
      assignment_id: assignmentId, answer_text: text,
    })
    setFeedback(f => ({ ...f, [assignmentId]: data }))
  }

  if (!assignments) return <Loading />
  const canManage = user.role === 'faculty' || user.role === 'admin'

  return (
    <div className="max-w-2xl mx-auto">
      <p className="eyebrow mb-1">Module 2 & 7 · Assignments + AI Evaluation</p>
      <h1 className="text-3xl font-semibold mb-6">Assignments</h1>

      {canManage && (
        <form onSubmit={createAssignment} className="card mb-6 space-y-3">
          <h3 className="font-semibold">New assignment</h3>
          <input className="input" placeholder="Title" required value={form.title}
            onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
          <textarea className="input" rows={3} placeholder="Instructions" value={form.instructions}
            onChange={e => setForm(f => ({ ...f, instructions: e.target.value }))} />
          <button className="btn-accent">Create</button>
        </form>
      )}

      <div className="space-y-4">
        {assignments.map(a => (
          <div key={a.id} className="card">
            <h3 className="font-semibold">{a.title}</h3>
            <p className="text-sm text-ink/60 mt-1">{a.instructions}</p>

            {user.role === 'student' && (
              <div className="mt-3">
                <textarea
                  className="input" rows={4} placeholder="Write your answer…"
                  value={answerDrafts[a.id] || ''}
                  onChange={e => setAnswerDrafts(d => ({ ...d, [a.id]: e.target.value }))}
                />
                <button className="btn-primary mt-2" onClick={() => submit(a.id)}>Submit for AI feedback</button>

                {feedback[a.id] && (
                  <div className="mt-3 p-3 bg-amber/10 rounded-md text-sm space-y-1">
                    <p className="font-medium">Preliminary AI feedback (not a final grade):</p>
                    <p>Relevance: {feedback[a.id].ai_relevance_score}/100 · Completeness: {feedback[a.id].ai_completeness_score}/100</p>
                    <p>Writing quality: {feedback[a.id].ai_writing_quality_score}/100 · Concept coverage: {feedback[a.id].ai_concept_coverage_score}/100</p>
                    <p className="text-ink/70">{feedback[a.id].ai_feedback}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
        {assignments.length === 0 && <p className="text-ink/50 text-sm">No assignments yet.</p>}
      </div>
    </div>
  )
}
