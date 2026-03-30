import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export async function uploadDocument(file: File) {
  const form = new FormData()
  form.append('file', file)
  const res = await api.post('/documents/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function getDocuments(params?: Record<string, string>) {
  const res = await api.get('/documents', { params })
  return res.data
}

export async function getDocument(id: string) {
  const res = await api.get(`/documents/${id}`)
  return res.data
}

export async function searchDocuments(query: string) {
  const res = await api.get('/search', { params: { q: query } })
  return res.data
}

export async function getStats() {
  const res = await api.get('/stats')
  return res.data
}

export default api
