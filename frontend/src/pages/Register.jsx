import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ full_name: '', email: '', password: '', confirmPassword: '', role: 'student' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  function update(k, v) { setForm(f => ({ ...f, [k]: v })) }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    // --- Client-side validation (fast feedback before hitting the API) ---
    const full_name = form.full_name.trim()
    const email = form.email.trim()

    if (!full_name || !email || !form.password || !form.confirmPassword) {
      setError('Please fill in all required fields')
      return
    }
    // Basic email shape check; the backend still re-validates with EmailStr.
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('Please enter a valid email address')
      return
    }
    if (form.password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setBusy(true)
    try {
      await register(full_name, email, form.password, form.role)
      navigate('/courses')
    } catch (err) {
      // Surface the backend's message (e.g. "Email already registered")
      // when available, otherwise a generic fallback.
      setError(err?.response?.data?.detail || 'Registration failed. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-10">
      <p className="eyebrow mb-2">Join Athenaeum</p>
      <h1 className="text-3xl font-semibold mb-6">Create your account</h1>
      <form onSubmit={handleSubmit} className="card space-y-4">
        <div>
          <label className="label">Full name</label>
          <input className="input" value={form.full_name} onChange={e => update('full_name', e.target.value)} required />
        </div>
        <div>
          <label className="label">Email</label>
          <input className="input" type="email" value={form.email} onChange={e => update('email', e.target.value)} required />
        </div>
        <div>
          <label className="label">Password</label>
          <input className="input" type="password" minLength={6} value={form.password} onChange={e => update('password', e.target.value)} required />
        </div>
        <div>
          <label className="label">Confirm password</label>
          <input className="input" type="password" minLength={6} value={form.confirmPassword} onChange={e => update('confirmPassword', e.target.value)} required />
        </div>
        <div>
          <label className="label">I am a</label>
          <select className="input" value={form.role} onChange={e => update('role', e.target.value)}>
            <option value="student">Student</option>
            <option value="faculty">Faculty</option>
            <option value="admin">Administrator</option>
          </select>
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button className="btn-primary w-full" disabled={busy}>{busy ? 'Creating…' : 'Create account'}</button>
      </form>
      <p className="text-sm text-ink/60 mt-4">
        Already registered? <Link className="text-amber font-medium" to="/login">Sign in</Link>
      </p>
    </div>
  )
}
