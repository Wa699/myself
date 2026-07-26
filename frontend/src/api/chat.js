import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

export async function sendMessage(sessionId, question) {
  const { data } = await api.post('/chat/messages', {
    sessionId: sessionId || null,
    question
  })
  return data
}
