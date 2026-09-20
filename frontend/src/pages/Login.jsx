import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('student@example.com')
  const [password, setPassword] = useState('password123')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      await login(email, password)
      navigate('/courses')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Sign in failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-10">
      <p className="eyebrow mb-2">Welcome back</p>
      <h1 className="text-3xl font-semibold mb-6">Sign in</h1>
      <form onSubmit={handleSubmit} className="card space-y-4">
        <div>
          <label className="label">Email</label>
          <input className="input" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <div>
          <label className="label">Password</label>
          <input className="input" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button className="btn-primary w-full" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
      </form>
      <p className="text-sm text-ink/60 mt-4">
        No account? <Link className="text-amber font-medium" to="/register">Create one</Link>
      </p>
      <p className="text-xs text-ink/40 mt-6">
        Demo accounts (after running seed.py): faculty@example.com, admin@example.com,
        student@example.com — all with password "password123".
      </p>
    </div>
  )
}
