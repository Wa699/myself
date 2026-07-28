<template>
  <div class="chat-window">
    <div class="messages" ref="messagesContainer">
      <!-- 空状态 -->
      <div v-if="messages.length === 0 && !streaming" class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <p class="empty-title">开始对话</p>
        <p class="empty-desc">在下方输入问题，了解候选人的技能、项目和经历</p>
      </div>

      <!-- 消息列表 -->
      <div v-for="(msg, i) in messages" :key="i" :class="['message-wrapper', msg.role]">
        <div class="message-avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
        <div class="message-body">
          <div :class="['message-bubble', msg.role]">
            <div class="message-content" v-html="renderMd(msg.content)"></div>
          </div>
          <!-- 引用来源 -->
          <div v-if="msg.citations && msg.citations.length > 0" class="citations">
            <div class="citation-label">📎 参考来源</div>
            <div v-for="(cite, j) in msg.citations" :key="j" class="citation-item">
              <span class="cite-category">{{ cite.category }}</span>
              <span class="cite-title">{{ cite.title }}</span>
              <p class="cite-excerpt">{{ cite.excerpt }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 流式输出 -->
      <div v-if="streaming" class="message-wrapper assistant">
        <div class="message-avatar">🤖</div>
        <div class="message-body">
          <div class="message-bubble assistant streaming">
            <div class="message-content" v-html="renderMd(streamingContent) + '<span class=cursor>|</span>'"></div>
          </div>
        </div>
      </div>

      <!-- 加载动画 -->
      <div v-else-if="loading" class="message-wrapper assistant">
        <div class="message-avatar">🤖</div>
        <div class="message-body">
          <div class="message-bubble assistant loading-bubble">
            <div class="typing-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <div class="input-wrapper">
        <input
          v-model="input"
          class="chat-input"
          placeholder="输入你的问题，按 Enter 发送..."
          @keyup.enter="handleSend"
          :disabled="loading"
        />
        <button
          class="send-btn"
          @click="handleSend"
          :disabled="loading || !input.trim()"
          title="发送"
        >
          <svg v-if="!loading" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M22 2L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M22 2L15 22l-4-9-9-4 20-9z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span v-else class="btn-loading-spinner"></span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { sendMessageStream } from '../api/chat.js'

// 简单 Markdown → HTML 渲染
function renderMd(text) {
  if (!text) return ''
  let html = text
    // 粗体
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 行内代码
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // 无序列表
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>')
    // 有序列表
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // 段落：双换行
    .replace(/\n\n/g, '</p><p>')
    // 单换行
    .replace(/\n/g, '<br>')
  html = '<p>' + html + '</p>'
  // 清理空标签
  html = html.replace(/<p>\s*<\/p>/g, '')
  html = html.replace(/<p><ul>/g, '<ul>')
  html = html.replace(/<\/ul><\/p>/g, '</ul>')
  return html
}

const props = defineProps({ sessionId: { type: String, default: null } })
const emit = defineEmits(['update:sessionId'])

const messages = ref([])
const input = ref('')
const loading = ref(false)
const streaming = ref(false)
const streamingContent = ref('')
const messagesContainer = ref(null)

// 生成 UUID v4（兼容非 HTTPS 环境）
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16)
  })
}

const sessionId = ref(props.sessionId || generateUUID())
onMounted(() => {
  emit('update:sessionId', sessionId.value)
})

async function scrollToBottom() {
  await nextTick()
  const el = messagesContainer.value
  if (el) {
    el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  }
}

async function handleSend() {
  const q = input.value.trim()
  if (!q || loading.value || streaming.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: q })
  streaming.value = true
  streamingContent.value = ''
  await scrollToBottom()

  // 构建历史：取最近 20 轮（40 条消息）
  const history = messages.value.slice(0, -1).slice(-40)

  sendMessageStream(
    q,
    sessionId.value,
    history,
    // onToken
    (token) => {
      streamingContent.value += token
      scrollToBottom()
    },
    // onDone
    (data) => {
      messages.value.push({
        role: 'assistant',
        content: streamingContent.value,
        citations: data.citations || []
      })
      streaming.value = false
      streamingContent.value = ''
      scrollToBottom()
    },
    // onError
    (errMsg) => {
      messages.value.push({
        role: 'assistant',
        content: errMsg,
        citations: []
      })
      streaming.value = false
      streamingContent.value = ''
      scrollToBottom()
    }
  )
}

async function sendQuestion(question) {
  input.value = question
  await handleSend()
}

defineExpose({ sendQuestion })
</script>

<style scoped>
.chat-window {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.07), 0 1px 4px rgba(0, 0, 0, 0.04);
}

/* ========== 消息区域 ========== */
.messages {
  height: 420px;
  overflow-y: auto;
  padding: 20px 20px 8px;
  background: linear-gradient(180deg, #fafbfd 0%, #f7f8fc 100%);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 70px 20px;
}
.empty-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f0f3ff 0%, #e8ecff 100%);
  color: #8899d8;
  margin-bottom: 16px;
}
.empty-icon svg {
  width: 28px;
  height: 28px;
}
.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 6px;
}
.empty-desc {
  font-size: 13px;
  color: #a0aec0;
}

/* 消息行 */
.message-wrapper {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  animation: messageIn 0.3s ease;
}
@keyframes messageIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.message-wrapper.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  background: #f2f4f8;
}
.message-wrapper.user .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.message-body {
  max-width: calc(100% - 50px);
  min-width: 0;
}
.message-wrapper.user .message-body {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

/* 气泡 */
.message-bubble {
  display: inline-block;
  padding: 10px 16px;
  font-size: 14px;
  line-height: 1.65;
  border-radius: 18px;
  word-break: break-word;
}
.message-bubble.user {
  background: linear-gradient(135deg, #667eea 0%, #5b6ce8 100%);
  color: #fff;
  border-bottom-right-radius: 6px;
}
.message-bubble.assistant {
  background: #fff;
  color: #2d3748;
  border: 1px solid #edf0f7;
  border-bottom-left-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.message-bubble.streaming {
  border: 1px solid #e4e8ff;
}

/* Markdown 内容 */
.message-content :deep(p) { margin: 0 0 6px; }
.message-content :deep(p:last-child) { margin-bottom: 0; }
.message-content :deep(ul), .message-content :deep(ol) { margin: 4px 0; padding-left: 20px; }
.message-content :deep(li) { margin: 3px 0; }
.message-content :deep(strong) { font-weight: 700; }
.message-content :deep(code) {
  background: rgba(0,0,0,0.08);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
}
.message-bubble.user .message-content :deep(code) {
  background: rgba(255,255,255,0.2);
}

/* 引用来源 */
.citations {
  margin-top: 8px;
  padding: 12px 14px;
  background: #fff;
  border-radius: 10px;
  border: 1px solid #eef1f7;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.citation-label {
  font-size: 12px;
  color: #8e99b0;
  margin-bottom: 6px;
  font-weight: 600;
}
.citation-item {
  font-size: 12px;
  margin: 6px 0;
  padding: 8px;
  background: #fafbfd;
  border-radius: 6px;
  border-left: 3px solid #667eea;
}
.cite-category {
  display: inline-block;
  padding: 2px 8px;
  background: linear-gradient(135deg, #eef1ff 0%, #e4e8ff 100%);
  color: #667eea;
  border-radius: 10px;
  margin-right: 8px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.3px;
}
.cite-title { color: #2d3748; font-weight: 600; }
.cite-excerpt { color: #718096; margin: 4px 0 0; font-size: 12px; line-height: 1.5; }

/* 流式光标 */
.cursor {
  display: inline-block;
  color: #667eea;
  animation: blink 0.8s step-end infinite;
  font-weight: 400;
  margin-left: 1px;
}
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

/* 打字动画 */
.typing-dots {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}
.typing-dots span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #bcc4d8;
  animation: dotBounce 1.3s ease infinite;
}
.typing-dots span:nth-child(1) { animation-delay: 0s; }
.typing-dots span:nth-child(2) { animation-delay: 0.15s; }
.typing-dots span:nth-child(3) { animation-delay: 0.3s; }
@keyframes dotBounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.35; }
  30%            { transform: translateY(-6px); opacity: 1; }
}
.loading-bubble {
  padding: 12px 16px;
}

/* ========== 输入区域 ========== */
.input-area {
  padding: 14px 18px;
  border-top: 1px solid #f0f2f7;
  background: #fff;
}
.input-wrapper {
  display: flex;
  gap: 10px;
  align-items: center;
  background: #f7f8fd;
  border-radius: 28px;
  padding: 5px 6px 5px 20px;
  border: 2px solid transparent;
  transition: border-color 0.25s, box-shadow 0.25s;
}
.input-wrapper:focus-within {
  border-color: #b4bef0;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.08);
}
.chat-input {
  flex: 1;
  padding: 10px 0;
  border: none;
  background: transparent;
  font-size: 14px;
  outline: none;
  color: #2d3748;
  min-width: 0;
}
.chat-input::placeholder { color: #bcc4d8; }
.chat-input:disabled { opacity: 0.5; }
.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}
.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 14px rgba(102, 126, 234, 0.4);
}
.send-btn:active:not(:disabled) {
  transform: scale(0.95);
}
.send-btn:disabled {
  background: #dce0ed;
  box-shadow: none;
  cursor: not-allowed;
}
.send-btn svg {
  width: 18px;
  height: 18px;
}

/* 发送按钮加载旋转 */
.btn-loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
