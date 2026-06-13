import { useState } from 'react'
import { useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import Dashboard from './pages/Dashboard'

export default function App() {
  const { user, loading } = useAuth()
  const [page, setPage] = useState('login')

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <span className="spinner" />
      </div>
    )
  }

  if (user) return <Dashboard />

  if (page === 'register') return <RegisterPage onSwitch={() => setPage('login')} />
  return <LoginPage onSwitch={() => setPage('register')} />
}
