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

export async function sendMessageStream(question, onToken, onDone, onError) {
  try {
    const resp = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    })

    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    // 用微延迟让逐字效果可见
    const delay = (ms) => new Promise(r => setTimeout(r, ms))

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const jsonStr = line.slice(6)
        try {
          const data = JSON.parse(jsonStr)
          if (data.done) {
            onDone(data)
          } else if (data.token) {
            onToken(data.token)
            await delay(15)  // 15ms 间隔，让视觉上看到逐字出现
          } else if (data.error) {
            onError(data.error)
          }
        } catch (e) {
          // 跳过解析失败的行
        }
      }
    }
  } catch (e) {
    onError(e.message || '网络错误，请稍后重试')
  }
}
