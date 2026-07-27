<template>
  <div class="chat-window">
    <div class="messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="empty-hint">
        在下方输入问题，了解候选人的技能、项目和经历
      </div>
      <div v-for="(msg, i) in messages" :key="i" :class="['message', msg.role]">
        <div class="message-content" v-html="renderMd(msg.content)"></div>
        <div v-if="msg.citations && msg.citations.length > 0" class="citations">
          <div class="citation-label">参考来源：</div>
          <div v-for="(cite, j) in msg.citations" :key="j" class="citation-item">
            <span class="cite-category">{{ cite.category }}</span>
            <span class="cite-title">{{ cite.title }}</span>
            <p class="cite-excerpt">{{ cite.excerpt }}</p>
          </div>
        </div>
      </div>
      <div v-if="streaming" class="message assistant">
        <div class="message-content" v-html="renderMd(streamingContent) + '<span class=cursor>|</span>'"></div>
      </div>
      <div v-else-if="loading" class="message assistant">
        <div class="loading-dots"><span>.</span><span>.</span><span>.</span></div>
      </div>
    </div>
    <div class="input-area">
      <input
        v-model="input"
        class="chat-input"
        placeholder="输入你的问题..."
        @keyup.enter="handleSend"
        :disabled="loading"
      />
      <button class="send-btn" @click="handleSend" :disabled="loading || !input.trim()">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { sendMessage, sendMessageStream } from '../api/chat.js'

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

async function scrollToBottom() {
  await nextTick()
  const el = messagesContainer.value
  if (el) el.scrollTop = el.scrollHeight
}

async function handleSend() {
  const q = input.value.trim()
  if (!q || loading.value || streaming.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: q })
  streaming.value = true
  streamingContent.value = ''
  await scrollToBottom()

  sendMessageStream(
    q,
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
  border: 1px solid #e8ecf1;
  border-radius: 8px;
  overflow: hidden;
}
.messages {
  height: 400px;
  overflow-y: auto;
  padding: 16px;
}
.empty-hint {
  text-align: center;
  color: #aaa;
  font-size: 14px;
  padding: 60px 0;
}
.message {
  margin-bottom: 16px;
  max-width: 85%;
}
.message.user { margin-left: auto; }
.message.user .message-content {
  background: #4a6cf7;
  color: #fff;
  border-radius: 12px 12px 2px 12px;
}
.message.assistant .message-content {
  background: #f2f4f8;
  border-radius: 12px 12px 12px 2px;
}
.message-content {
  padding: 10px 14px;
  font-size: 14px;
  line-height: 1.6;
}
.message.user .message-content {
  display: inline-block;
}
.message.assistant .message-content {
  display: block;
}
.message-content :deep(p) { margin: 0 0 8px; }
.message-content :deep(p:last-child) { margin-bottom: 0; }
.message-content :deep(ul), .message-content :deep(ol) { margin: 4px 0; padding-left: 18px; }
.message-content :deep(li) { margin: 2px 0; }
.message-content :deep(strong) { font-weight: 600; }
.message-content :deep(code) {
  background: #e8ecf1;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 13px;
  font-family: monospace;
}
.citations {
  margin-top: 6px;
  padding: 8px 12px;
  background: #fafbfc;
  border-radius: 6px;
  border: 1px solid #eef0f4;
}
.citation-label { font-size: 12px; color: #999; margin-bottom: 4px; }
.citation-item { font-size: 12px; margin: 4px 0; }
.cite-category {
  display: inline-block;
  padding: 1px 6px;
  background: #eef2ff;
  color: #4a6cf7;
  border-radius: 3px;
  margin-right: 6px;
  font-size: 11px;
}
.cite-title { color: #333; font-weight: 500; }
.cite-excerpt { color: #777; margin: 2px 0 0; font-size: 12px; }
.cursor {
  display: inline-block;
  color: #4a6cf7;
  animation: blink 1s step-end infinite;
  font-weight: 700;
}
.loading-dots span {
  display: inline-block;
  animation: blink 1.4s infinite both;
  font-size: 20px;
  color: #aaa;
}
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink { 0%, 80%, 100% { opacity: 0; } 40% { opacity: 1; } }
.input-area {
  display: flex;
  padding: 12px 16px;
  border-top: 1px solid #e8ecf1;
  gap: 8px;
}
.chat-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #dde4f0;
  border-radius: 20px;
  font-size: 14px;
  outline: none;
}
.chat-input:focus { border-color: #4a6cf7; }
.send-btn {
  padding: 10px 20px;
  background: #4a6cf7;
  color: #fff;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
}
.send-btn:disabled { background: #c4cfe0; cursor: not-allowed; }
</style>
