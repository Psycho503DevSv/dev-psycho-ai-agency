import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import CyberBackground from '../components/CyberBackground'
import { TiltCard, TextScramble } from '../components/CyberEffects'

export default function RegisterPage({ onSwitch }) {
  const { register } = useAuth()
  const [form, setForm] = useState({ email: '', username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password.length < 6) { setError('Password must be at least 6 characters'); return }
    setLoading(true)
    try {
      await register(form.email, form.username, form.password)
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
          <span style={{ fontSize: '0.7rem', color: 'var(--accent-purple)', border: '1px solid var(--accent-purple)', padding: '2px 6px', textTransform: 'uppercase' }}>
            REG_MODE_AUTO
          </span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>ID_REG_2085</span>
        </div>

        <h1 className="auth-title">
          <TextScramble text="NEW_AI_ENTITY" />
        </h1>
        <div className="auth-sub">INITIALIZE COGNITIVE PROFILE REGISTRATION</div>

        {error && (
          <div className="alert alert-error">
            <span style={{ fontWeight: 'bold' }}>[ERR_PROFILE_FAIL]</span> {error}
          </div>
        )}

        <form onSubmit={submit}>
          <div className="form-group">
            <label htmlFor="reg-email">[COGNITIVE_NODE_EMAIL]</label>
            <input id="reg-email" type="email" value={form.email} onChange={set('email')} placeholder="operator@classified.mil" required />
          </div>
          <div className="form-group">
            <label htmlFor="reg-username">[CALLSIGN_NAME]</label>
            <input id="reg-username" type="text" value={form.username} onChange={set('username')} placeholder="operator_omega" required />
          </div>
          <div className="form-group">
            <label htmlFor="reg-password">[CRYPTOGRAPHIC_KEY]</label>
            <input id="reg-password" type="password" value={form.password} onChange={set('password')} placeholder="Min. 6 characters" required />
          </div>
          <button className="btn btn-primary btn-full" type="submit" disabled={loading} style={{ marginTop: '1rem' }}>
            {loading ? <span className="spinner" /> : 'REGISTER_PROFILE'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          ALREADY AUTHORIZED PROFILE?{' '}
          <button className="link-btn" onClick={onSwitch} style={{ fontSize: '0.8rem' }}>PROCEED_TO_AUTH</button>
        </p>
      </TiltCard>
    </div>
  )
}
