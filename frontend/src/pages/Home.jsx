import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const FEATURES = [
  { title: 'AI Learning Assistant', desc: 'Ask questions in plain language — answers are grounded in your actual course material via Retrieval-Augmented Generation, with sources cited.' },
  { title: 'Personalized Learning Paths', desc: 'Recommendations for what to study next, generated from your real quiz and engagement data.' },
  { title: 'Knowledge Graph Navigation', desc: 'Explore how concepts, prerequisites, and learning outcomes connect across a course.' },
  { title: 'AI Study Material Generator', desc: 'Turn any uploaded PDF or slide deck into summaries, flashcards, quizzes, and revision notes.' },
  { title: 'Explainable Learning Analytics', desc: 'Performance predictions come with the reasoning behind them, not just a number.' },
  { title: 'Semantic Search', desc: 'Search by meaning, not keywords — find the right lecture note even if the exact phrase never appears.' },
]

export default function Home() {
  const { user } = useAuth()
  return (
    <div>
      <section className="py-10 sm:py-16">
        <p className="eyebrow mb-3">AI-Powered Intelligent E-Learning Platform</p>
        <h1 className="text-4xl sm:text-5xl font-semibold leading-tight max-w-2xl">
          A learning platform that actually understands your course material.
        </h1>
        <p className="mt-4 text-ink/70 max-w-xl">
          Athenaeum pairs Large Language Models with Retrieval-Augmented Generation,
          a Knowledge Graph, and Explainable AI — so every answer, recommendation,
          and prediction is grounded and transparent.
        </p>
        <div className="mt-6 flex gap-3">
          {user ? (
            <Link to="/courses" className="btn-accent">Go to your courses</Link>
          ) : (
            <>
              <Link to="/register" className="btn-accent">Get started</Link>
              <Link to="/login" className="btn-ghost">Sign in</Link>
            </>
          )}
        </div>
      </section>

      <section className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 py-8">
        {FEATURES.map((f) => (
          <div key={f.title} className="card">
            <h3 className="font-semibold mb-1">{f.title}</h3>
            <p className="text-sm text-ink/60">{f.desc}</p>
          </div>
        ))}
      </section>
    </div>
  )
}
