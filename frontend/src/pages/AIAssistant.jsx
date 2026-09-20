import React, { useEffect, useRef, useState } from 'react'
import client from '../api/client'
import ConfidenceBadge from '../components/ConfidenceBadge'

export default function AIAssistant() {
  const [courses, setCourses] = useState([])
  const [courseId, setCourseId] = useState('')
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [busy, setBusy] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    client.get('/api/courses').then(r => setCourses(r.data))
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function ask(e) {
    e.preventDefault()
    if (!question.trim()) return
    const q = question
    setQuestion('')
    setMessages(m => [...m, { role: 'user', content: q }])
    setBusy(true)
    try {
      const { data } = await client.post('/api/assistant/ask', {
        course_id: courseId ? Number(courseId) : null,
        question: q,
      })
      setMessages(m => [...m, { role: 'assistant', content: data.answer, sources: data.sources, confidence: data.confidence }])
    } catch (err) {
      setMessages(m => [...m, { role: 'assistant', content: 'Sorry — something went wrong reaching the AI backend. Check that your LLM_PROVIDER is configured in .env.', error: true }])
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <p className="eyebrow mb-1">Module 6 · Retrieval-Augmented Generation</p>
      <h1 className="text-3xl font-semibold mb-4">AI Learning Assistant</h1>

      <div className="mb-4">
        <label className="label">Scope to a course (recommended for grounded answers)</label>
        <select className="input" value={courseId} onChange={e => setCourseId(e.target.value)}>
          <option value="">No course — general question</option>
          {courses.map(c => <option key={c.id} value={c.id}>{c.code} — {c.title}</option>)}
        </select>
      </div>

      <div className="card min-h-[320px] max-h-[50vh] overflow-y-auto flex flex-col gap-3 mb-4">
        {messages.length === 0 && (
          <p className="text-ink/40 text-sm text-center my-auto">
            Ask a question about your course material — e.g. "Explain routing algorithms".
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`max-w-[85%] ${m.role === 'user' ? 'self-end text-right' : 'self-start'}`}>
            <div className={`rounded-lg px-3 py-2 text-sm inline-block text-left ${
              m.role === 'user' ? 'bg-ink text-parchment' : m.error ? 'bg-red-50 text-red-700' : 'bg-amber/10'
            }`}>
              {m.content}
            </div>
            {m.role === 'assistant' && !m.error && (
              <div className="mt-1 flex flex-wrap items-center gap-2">
                <ConfidenceBadge score={m.confidence} />
                {m.sources?.length > 0 && (
                  <span className="text-[11px] text-ink/50">
                    Sources: {m.sources.map(s => s.title).join(', ')}
                  </span>
                )}
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={ask} className="flex gap-2">
        <input
          className="input flex-1"
          placeholder="Ask anything about your course…"
          value={question}
          onChange={e => setQuestion(e.target.value)}
        />
        <button className="btn-accent" disabled={busy}>{busy ? 'Thinking…' : 'Ask'}</button>
      </form>
    </div>
  )
}
