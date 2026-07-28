<template>
  <div class="app-container">
    <header class="app-header">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L2 7l10 5 10-5-10-5z" fill="currentColor" opacity="0.7"/>
          <path d="M2 17l10 5 10-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h1>候选人简历问答</h1>
      <p class="app-subtitle">基于候选人资料，智能回答面试相关问题</p>
    </header>
    <ProfileCard />
    <SampleQuestions @select="handleSelectQuestion" />
    <ChatWindow ref="chatWindow" :session-id="sessionId" @update:session-id="sessionId = $event" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ProfileCard from './components/ProfileCard.vue'
import SampleQuestions from './components/SampleQuestions.vue'
import ChatWindow from './components/ChatWindow.vue'

const sessionId = ref(null)
const chatWindow = ref(null)

function handleSelectQuestion(question) {
  chatWindow.value?.sendQuestion(question)
}
</script>

<style scoped>
.app-container {
  max-width: 720px;
  margin: 0 auto;
  padding: 32px 16px 48px;
}
.app-header {
  text-align: center;
  padding: 32px 0 24px;
}
.header-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  margin-bottom: 16px;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.35);
}
.header-icon svg {
  width: 28px;
  height: 28px;
}
.app-header h1 {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #2d3a5c 0%, #4a5f8a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.app-subtitle {
  font-size: 14px;
  color: #8e99b0;
  margin-top: 6px;
  letter-spacing: 0.3px;
}
</style>
