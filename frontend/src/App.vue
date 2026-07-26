<template>
  <div class="app-container">
    <header class="app-header">
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
  padding: 20px 16px 40px;
}
.app-header {
  text-align: center;
  padding: 24px 0 16px;
}
.app-header h1 {
  font-size: 22px;
  font-weight: 600;
  color: #1a1a2e;
}
.app-subtitle {
  font-size: 14px;
  color: #888;
  margin-top: 4px;
}
</style>
