import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <header className="border-b border-ink/10 bg-parchment/95 backdrop-blur sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-baseline gap-2">
          <span className="font-display text-xl font-semibold">Athenaeum</span>
          <span className="text-[10px] uppercase tracking-[0.2em] text-ink/40">AI Learning Platform</span>
        </Link>

        {user ? (
          <nav className="flex items-center gap-1 sm:gap-2 text-sm">
            <Link className="btn-ghost !px-3 !py-1.5" to="/courses">Courses</Link>
            {user.role === 'student' && (
              <>
                <Link className="btn-ghost !px-3 !py-1.5" to="/assistant">AI Assistant</Link>
                <Link className="btn-ghost !px-3 !py-1.5" to="/analytics">My Progress</Link>
              </>
            )}
            {(user.role === 'faculty' || user.role === 'admin') && (
              <Link className="btn-ghost !px-3 !py-1.5" to="/admin">Dashboard</Link>
            )}
            <span className="hidden sm:inline text-ink/50 text-xs px-2">
              {user.full_name} · {user.role}
            </span>
            <button onClick={handleLogout} className="btn-accent !px-3 !py-1.5">Sign out</button>
          </nav>
        ) : (
          <nav className="flex items-center gap-2">
            <Link className="btn-ghost" to="/login">Sign in</Link>
            <Link className="btn-accent" to="/register">Get started</Link>
          </nav>
        )}
      </div>
    </header>
  )
}
