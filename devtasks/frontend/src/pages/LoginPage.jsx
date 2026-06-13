import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import CyberBackground from '../components/CyberBackground'
import { TiltCard, TextScramble } from '../components/CyberEffects'

export default function LoginPage({ onSwitch }) {
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrap">
      <CyberBackground />
      <TiltCard className="auth-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--accent)', border: '1px solid var(--accent)', padding: '2px 6px', textTransform: 'uppercase' }}>
            SEC_LEVEL_05
          </span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>SYS_REF_2085</span>
        </div>

        <h1 className="auth-title">
          <TextScramble text="AI_CORE_AUTH" />
        </h1>
        <div className="auth-sub">INITIALIZE EXPERIMENTAL SECURITY DECRYPTOR</div>

        {error && (
          <div className="alert alert-error">
            <span style={{ fontWeight: 'bold' }}>[ERR_AUTH_REJECTED]</span> {error}
          </div>
        )}

        <form onSubmit={submit}>
          <div className="form-group">
            <label htmlFor="login-email">[USERID_IDENTIFIER]</label>
            <input
              id="login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="operator@classified.mil"
              required
              autoFocus
            />
          </div>
          <div className="form-group">
            <label htmlFor="login-password">[KEY_PASSPHRASE]</label>
            <input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>
          <button className="btn btn-primary btn-full" type="submit" disabled={loading} style={{ marginTop: '1rem' }}>
            {loading ? <span className="spinner" /> : 'DECRYPT_ACCESS'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          NO PERMISSION PROFILE FOUND?{' '}
          <button className="link-btn" onClick={onSwitch} style={{ fontSize: '0.8rem' }}>REQUEST_CREDENTIALS</button>
        </p>
      </TiltCard>
    </div>
  )
}
