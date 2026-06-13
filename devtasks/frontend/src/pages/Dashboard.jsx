import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { api } from '../api'
import CyberBackground from '../components/CyberBackground'
import { TiltCard, TextScramble } from '../components/CyberEffects'

const STATUS_OPTIONS = ['todo', 'in_progress', 'done']
const STATUS_LABELS = { todo: 'QUEUE', in_progress: 'ACTIVE', done: 'COMPILED' }

function TaskModal({ task, onClose, onSaved }) {
  const [form, setForm] = useState({ title: task?.title || '', description: task?.description || '', status: task?.status || 'todo' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    if (!form.title.trim()) { setError('Title is required'); return }
    setLoading(true)
    try {
      if (task) {
        await api.updateTask(task.id, form)
      } else {
        await api.createTask({ title: form.title, description: form.description })
      }
      onSaved()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <span className="modal-title" style={{ fontFamily: 'Orbitron', letterSpacing: '2px' }}>
            <TextScramble text={task ? 'EDIT_INTELLIGENCE_MODULE' : 'NEW_INTELLIGENCE_MODULE'} />
          </span>
          <button className="btn btn-ghost" onClick={onClose} style={{ padding: '0.2rem 0.5rem', fontFamily: 'monospace' }}>✕</button>
        </div>
        {error && <div className="alert alert-error">[SYS_ERR] {error}</div>}
        <form onSubmit={submit}>
          <div className="form-group">
            <label htmlFor="task-title">[MODULE_NAME]</label>
            <input id="task-title" value={form.title} onChange={set('title')} placeholder="Enter identifier..." autoFocus />
          </div>
          <div className="form-group">
            <label htmlFor="task-desc">[DESCRIPTIVE_PARAMETERS]</label>
            <textarea id="task-desc" value={form.description} onChange={set('description')} placeholder="Operational notes..." />
          </div>
          {task && (
            <div className="form-group">
              <label htmlFor="task-status">[COGNITIVE_STATE]</label>
              <select id="task-status" value={form.status} onChange={set('status')}>
                {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
              </select>
            </div>
          )}
          <div className="modal-footer">
            <button type="button" className="btn btn-ghost" onClick={onClose}>ABORT</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? <span className="spinner" /> : task ? 'UPDATE_MODULE' : 'DEPLOY_MODULE'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(null) // null | 'new' | task object
  const [filter, setFilter] = useState('all')
  const [simulatedLoad, setSimulatedLoad] = useState(42.5)
  const [simulatedTemp, setSimulatedTemp] = useState(38.0)

  const fetchTasks = useCallback(async () => {
    try {
      const data = await api.tasks()
      setTasks(data)
    } catch (_) {}
    finally { setLoading(false) }
  }, [])

  useEffect(() => {
    fetchTasks()
    
    // Simulate real-time military AI command center metrics fluctuability
    const interval = setInterval(() => {
      setSimulatedLoad((prev) => Math.max(25, Math.min(99, +(prev + (Math.random() - 0.5) * 8).toFixed(1))))
      setSimulatedTemp((prev) => Math.max(30, Math.min(85, +(prev + (Math.random() - 0.5) * 2).toFixed(1))))
    }, 2000)

    return () => clearInterval(interval)
  }, [fetchTasks])

  const handleDelete = async (id) => {
    if (!confirm('Abort/purge this intelligence module?')) return
    await api.deleteTask(id)
    setTasks((t) => t.filter((x) => x.id !== id))
  }

  const filtered = filter === 'all' ? tasks : tasks.filter((t) => t.status === filter)
  const counts = { todo: 0, in_progress: 0, done: 0 }
  tasks.forEach((t) => counts[t.status]++)

  return (
    <div className="app">
      <CyberBackground />
      <nav className="navbar">
        <span className="navbar-brand">
          <span style={{ animation: 'spin 4s linear infinite', marginRight: '6px', fontSize: '1.2rem' }}>☢</span>
          NEURAL_NET_2085
        </span>
        <div className="navbar-actions">
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', marginRight: '10px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--accent)', fontWeight: 'bold' }}>CALLSIGN: {user?.username}</span>
            <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>ROLE: {user?.role || 'OPERATOR'}</span>
          </div>
          <button className="btn btn-ghost" style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem' }} onClick={logout}>DISCONNECT</button>
        </div>
      </nav>

      <main className="main">
        {/* Core Tactical Status panels */}
        <div className="stats">
          <TiltCard className="card stat-card" style={{ borderLeft: '3px solid var(--text-muted)' }}>
            <div className="stat-num">{counts.todo}</div>
            <div className="stat-label">QUEUE / TO DO</div>
          </TiltCard>
          <TiltCard className="card stat-card" style={{ borderLeft: '3px solid var(--warn)' }}>
            <div className="stat-num" style={{ color: 'var(--warn)', textShadow: '0 0 10px rgba(255,183,0,0.4)' }}>{counts.in_progress}</div>
            <div className="stat-label">ACTIVE COGNITION</div>
          </TiltCard>
          <TiltCard className="card stat-card" style={{ borderLeft: '3px solid var(--success)' }}>
            <div className="stat-num" style={{ color: 'var(--success)', textShadow: '0 0 10px rgba(0,255,102,0.4)' }}>{counts.done}</div>
            <div className="stat-label">COMPILED SEQUENCES</div>
          </TiltCard>
        </div>

        {/* Dashboard Grid layout */}
        <div className="dashboard-grid">
          {/* Main Intelligence Queue */}
          <div>
            <div className="dashboard-header">
              <h2 className="dashboard-title">
                <TextScramble text="TACTICAL_INTELLIGENCE_MODULES" />
              </h2>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <select value={filter} onChange={(e) => setFilter(e.target.value)} style={{ width: 'auto', padding: '0.4rem 0.8rem', fontFamily: 'monospace' }}>
                  <option value="all">ALL_MODULES</option>
                  {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
                </select>
                <button className="btn btn-primary" onClick={() => setModal('new')} id="new-task-btn" style={{ padding: '0.4rem 1rem' }}>
                  + DEPLOY_INTEL
                </button>
              </div>
            </div>

            {loading ? (
              <div className="flex-center" style={{ padding: '3rem' }}><span className="spinner" /></div>
            ) : filtered.length === 0 ? (
              <div className="empty">
                <div className="empty-icon" style={{ animation: 'spin 10s linear infinite' }}>⚙</div>
                <div className="empty-text" style={{ fontStyle: 'italic', letterSpacing: '2px' }}>
                  {filter === 'all' ? '[NO MODULES DEPLOYED IN THIS SYSTEM]' : `[NO MODULES COMPLYING WITH STATE "${STATUS_LABELS[filter]}"]`}
                </div>
              </div>
            ) : (
              <div className="task-grid">
                {filtered.map((task) => (
                  <TiltCard key={task.id} className="card task-card">
                    <div className="task-info">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '0.6rem', color: 'var(--accent)', border: '1px solid var(--border)', padding: '1px 4px' }}>
                          SYS_ID_{task.id}
                        </span>
                        <span className="task-title">{task.title}</span>
                      </div>
                      {task.description && (
                        <div className="task-desc" style={{ marginTop: '0.25rem', fontFamily: 'monospace', opacity: 0.85 }}>
                          &gt; {task.description}
                        </div>
                      )}
                      <div className="task-meta">
                        <span className={`badge badge-${task.status}`}>{STATUS_LABELS[task.status]}</span>
                        <span style={{ color: 'var(--text-muted)' }}>SECTOR: DELTA_9</span>
                      </div>
                    </div>
                    <div className="task-actions">
                      <button className="btn btn-ghost" style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }} onClick={() => setModal(task)}>RECONFIGURE</button>
                      <button className="btn btn-danger" style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }} onClick={() => handleDelete(task.id)}>PURGE</button>
                    </div>
                  </TiltCard>
                ))}
              </div>
            )}
          </div>

          {/* Right Column: AI Diagnostics Sidebar */}
          <div className="tactical-sidebar">
            <TiltCard className="tactical-panel">
              <h3 className="panel-title">AI_CORE_DIAGNOSTICS</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.8rem', fontFamily: 'monospace' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>COGNITIVE_LOAD:</span>
                  <span style={{ color: simulatedLoad > 80 ? 'var(--danger)' : 'var(--accent)' }}>{simulatedLoad}%</span>
                </div>
                <div style={{ width: '100%', height: '4px', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--border)' }}>
                  <div style={{ width: `${simulatedLoad}%`, height: '100%', background: 'var(--accent)', boxShadow: 'var(--glow-cyan)', transition: 'width 2s ease' }} />
                </div>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>CORE_TEMPERATURE:</span>
                  <span style={{ color: simulatedTemp > 70 ? 'var(--danger)' : 'var(--accent-purple)' }}>{simulatedTemp}°C</span>
                </div>
                <div style={{ width: '100%', height: '4px', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--border)' }}>
                  <div style={{ width: `${(simulatedTemp / 100) * 100}%`, height: '100%', background: 'var(--accent-purple)', boxShadow: 'var(--glow-purple)', transition: 'width 2s ease' }} />
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>ENCRYPTION_INDEX:</span>
                  <span style={{ color: 'var(--success)' }}>AES_256_GCM</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>COGNITIVE_SHARDS:</span>
                  <span style={{ color: 'var(--accent)' }}>{tasks.length} / 256</span>
                </div>
              </div>
            </TiltCard>

            <TiltCard className="tactical-panel">
              <h3 className="panel-title">SYSTEM_LOG_STREAM</h3>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'monospace', maxHeight: '150px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div>[15:12:44] SYS: CONNECTION STABLISHED</div>
                <div>[15:12:46] SEC: CORRUPT MEMORY BYPASSED</div>
                <div>[15:13:01] AI: KERNEL INTEGRITY VERIFIED</div>
                <div>[15:13:58] USER: DIRECTIVES REGISTERED</div>
                <div>[15:14:12] COMPILING COGNITIVE MATRICES...</div>
                <div style={{ color: 'var(--accent)' }}>&gt; SHARDS SYNCHRONIZED [OK]</div>
              </div>
            </TiltCard>
          </div>
        </div>
      </main>

      {modal && (
        <TaskModal
          task={modal === 'new' ? null : modal}
          onClose={() => setModal(null)}
          onSaved={() => { setModal(null); fetchTasks() }}
        />
      )}
    </div>
  )
}
