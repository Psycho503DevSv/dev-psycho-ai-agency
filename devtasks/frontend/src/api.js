const BASE_URL = import.meta.env.VITE_API_URL || '/api'

async function request(path, options = {}) {
  const token = localStorage.getItem('token')
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  if (!res.ok) {
    let msg = `Error ${res.status}`
    try { const d = await res.json(); msg = d.detail || msg } catch (_) {}
    throw new Error(msg)
  }
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  me: () => request('/users/me'),
  users: () => request('/users/'),
  tasks: () => request('/tasks/'),
  createTask: (data) => request('/tasks/', { method: 'POST', body: JSON.stringify(data) }),
  updateTask: (id, data) => request(`/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteTask: (id) => request(`/tasks/${id}`, { method: 'DELETE' }),
}
