import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { api } from '../api'

const STATUS_OPTIONS = ['todo', 'in_progress', 'done']
const STATUS_LABELS = { todo: 'To Do', in_progress: 'In Progress', done: 'Done' }

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
          <span className="modal-title">{task ? 'Edit Task' : 'New Task'}</span>
          <button className="btn btn-ghost" onClick={onClose} style={{ padding: '0.3rem 0.6rem' }}>✕</button>
        </div>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={submit}>
          <div className="form-group">
            <label htmlFor="task-title">Title</label>
            <input id="task-title" value={form.title} onChange={set('title')} placeholder="Task title" autoFocus />
          </div>
          <div className="form-group">
            <label htmlFor="task-desc">Description</label>
            <textarea id="task-desc" value={form.description} onChange={set('description')} placeholder="Optional description..." />
          </div>
          {task && (
            <div className="form-group">
              <label htmlFor="task-status">Status</label>
              <select id="task-status" value={form.status} onChange={set('status')}>
                {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
              </select>
            </div>
          )}
          <div className="modal-footer">
            <button type="button" className="btn btn-ghost" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? <span className="spinner" /> : task ? 'Save Changes' : 'Create Task'}
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

  const fetchTasks = useCallback(async () => {
    try {
      const data = await api.tasks()
      setTasks(data)
    } catch (_) {}
    finally { setLoading(false) }
  }, [])

  useEffect(() => { fetchTasks() }, [fetchTasks])

  const handleDelete = async (id) => {
    if (!confirm('Delete this task?')) return
    await api.deleteTask(id)
    setTasks((t) => t.filter((x) => x.id !== id))
  }

  const filtered = filter === 'all' ? tasks : tasks.filter((t) => t.status === filter)
  const counts = { todo: 0, in_progress: 0, done: 0 }
  tasks.forEach((t) => counts[t.status]++)

  return (
    <div className="app">
      <nav className="navbar">
        <span className="navbar-brand">⚡ DevTasks</span>
        <div className="navbar-actions">
          <span className="text-muted">{user?.username}</span>
          {user?.role === 'admin' && <span className="badge badge-in_progress">Admin</span>}
          <button className="btn btn-ghost" onClick={logout}>Sign Out</button>
        </div>
      </nav>

      <main className="main">
        <div className="stats">
          <div className="card stat-card">
            <div className="stat-num">{counts.todo}</div>
            <div className="stat-label">To Do</div>
          </div>
          <div className="card stat-card">
            <div className="stat-num" style={{ color: 'var(--warn)' }}>{counts.in_progress}</div>
            <div className="stat-label">In Progress</div>
          </div>
          <div className="card stat-card">
            <div className="stat-num" style={{ color: 'var(--success)' }}>{counts.done}</div>
            <div className="stat-label">Done</div>
          </div>
        </div>

        <div className="dashboard-header">
          <h1 className="dashboard-title">My Tasks</h1>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <select value={filter} onChange={(e) => setFilter(e.target.value)} style={{ width: 'auto' }}>
              <option value="all">All</option>
              {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
            </select>
            <button className="btn btn-primary" onClick={() => setModal('new')} id="new-task-btn">+ New Task</button>
          </div>
        </div>

        {loading ? (
          <div className="flex-center" style={{ padding: '3rem' }}><span className="spinner" /></div>
        ) : filtered.length === 0 ? (
          <div className="empty">
            <div className="empty-icon">📋</div>
            <div className="empty-text">{filter === 'all' ? 'No tasks yet. Create your first one!' : `No tasks with status "${STATUS_LABELS[filter]}"`}</div>
          </div>
        ) : (
          <div className="task-grid">
            {filtered.map((task) => (
              <div key={task.id} className="card task-card">
                <div className="task-info">
                  <div className="task-title">{task.title}</div>
                  {task.description && <div className="task-desc">{task.description}</div>}
                  <div className="task-meta">
                    <span className={`badge badge-${task.status}`}>{STATUS_LABELS[task.status]}</span>
                    <span className="text-muted">#{task.id}</span>
                  </div>
                </div>
                <div className="task-actions">
                  <button className="btn btn-ghost" style={{ padding: '0.4rem 0.8rem', fontSize: '0.82rem' }} onClick={() => setModal(task)}>Edit</button>
                  <button className="btn btn-danger" style={{ padding: '0.4rem 0.8rem', fontSize: '0.82rem' }} onClick={() => handleDelete(task.id)}>Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
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
