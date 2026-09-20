import React, { createContext, useContext, useEffect, useState } from 'react'
import client from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('user')
    return raw ? JSON.parse(raw) : null
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (user) localStorage.setItem('user', JSON.stringify(user))
  }, [user])

  async function login(email, password) {
    setLoading(true)
    try {
      const { data } = await client.post('/api/auth/login', { email, password })
      localStorage.setItem('token', data.access_token)
      setUser(data.user)
      return data.user
    } finally {
      setLoading(false)
    }
  }

  async function register(full_name, email, password, role) {
    setLoading(true)
    try {
      const { data } = await client.post('/api/auth/register', { full_name, email, password, role })
      localStorage.setItem('token', data.access_token)
      setUser(data.user)
      return data.user
    } finally {
      setLoading(false)
    }
  }

  function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
