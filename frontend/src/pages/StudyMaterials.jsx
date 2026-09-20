import React, { useState } from 'react'
import { useParams } from 'react-router-dom'
import client from '../api/client'
import Loading from '../components/Loading'

const KINDS = [
  { key: 'summary', label: 'Summary' },
  { key: 'flashcards', label: 'Flashcards' },
  { key: 'quiz', label: 'Quiz' },
  { key: 'revision_notes', label: 'Revision notes' },
]

export default function StudyMaterials() {
  const { materialId } = useParams()
  const [active, setActive] = useState('summary')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  // quiz-taking state
  const [quizId, setQuizId] = useState(null)
  const [answers, setAnswers] = useState({})
  const [quizResult, setQuizResult] = useState(null)

  async function generate(kind) {
    setActive(kind)
    setBusy(true)
    setError('')
    setResult(null)
    setQuizResult(null)
    setAnswers({})
    try {
      const { data } = await client.post('/api/study/generate', {
        material_id: Number(materialId), kind, num_items: 6,
      })
      setResult(data.content)
      if (kind === 'quiz') setQuizId(data.quiz_id)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Generation failed — check your LLM provider configuration.')
    } finally {
      setBusy(false)
    }
  }

  async function submitQuiz() {
    const ordered = result.map((_, i) => answers[i] ?? -1)
    const { data } = await client.post('/api/study/quizzes/submit', { quiz_id: quizId, answers: ordered })
    setQuizResult(data)
  }

  return (
    <div className="max-w-3xl mx-auto">
      <p className="eyebrow mb-1">Module 4 · AI Study Material Generator</p>
      <h1 className="text-3xl font-semibold mb-6">Study tools</h1>

      <div className="flex flex-wrap gap-2 mb-6">
        {KINDS.map(k => (
          <button key={k.key} onClick={() => generate(k.key)}
            className={active === k.key ? 'btn-accent text-sm' : 'btn-ghost text-sm'}>
            {k.label}
          </button>
        ))}
      </div>

      {busy && <Loading label="Generating with AI…" />}
      {error && <p className="text-sm text-red-600 mb-4">{error}</p>}

      {!busy && result && active === 'summary' && (
        <div className="card whitespace-pre-wrap leading-relaxed">{result}</div>
      )}

      {!busy && result && active === 'revision_notes' && (
        <div className="card whitespace-pre-wrap leading-relaxed">{result}</div>
      )}

      {!busy && result && active === 'flashcards' && (
        <div className="grid sm:grid-cols-2 gap-3">
          {result.map((f, i) => <Flashcard key={i} q={f.question} a={f.answer} />)}
        </div>
      )}

      {!busy && result && active === 'quiz' && !quizResult && (
        <div className="space-y-4">
          {result.map((q, i) => (
            <div key={i} className="card">
              <p className="font-medium mb-2">{i + 1}. {q.question}</p>
              <div className="space-y-1">
                {q.options.map((opt, oi) => (
                  <label key={oi} className="flex items-center gap-2 text-sm">
                    <input type="radio" name={`q${i}`} checked={answers[i] === oi}
                      onChange={() => setAnswers(a => ({ ...a, [i]: oi }))} />
                    {opt}
                  </label>
                ))}
              </div>
            </div>
          ))}
          <button className="btn-primary" onClick={submitQuiz}>Submit quiz</button>
        </div>
      )}

      {quizResult && (
        <div className="card">
          <h3 className="font-semibold text-lg mb-2">
            Score: {quizResult.score_percent}% ({quizResult.correct_count}/{quizResult.total})
          </h3>
          <div className="space-y-3 mt-3">
            {quizResult.review.map((r, i) => (
              <div key={i} className={`p-3 rounded-md text-sm ${r.is_correct ? 'bg-moss/10' : 'bg-red-50'}`}>
                <p className="font-medium">{r.question}</p>
                <p className="text-ink/60 mt-1">{r.explanation}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function Flashcard({ q, a }) {
  const [flipped, setFlipped] = useState(false)
  return (
    <button onClick={() => setFlipped(f => !f)} className="card text-left hover:shadow-md transition-shadow">
      <p className="text-[10px] uppercase tracking-wide text-amber mb-1">{flipped ? 'Answer' : 'Question'}</p>
      <p className="text-sm">{flipped ? a : q}</p>
    </button>
  )
}
