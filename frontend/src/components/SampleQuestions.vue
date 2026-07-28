<template>
  <div class="sample-questions" v-if="questions.length">
    <div class="sq-header">
      <h3 class="sq-title">💡 试试这些问题</h3>
    </div>
    <div class="sq-list">
      <button v-for="q in questions" :key="q" class="sq-chip" @click="$emit('select', q)">{{ q }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

defineEmits(['select'])
const questions = ref([])

onMounted(async () => {
  try {
    const resp = await fetch('/api/sample-questions')
    const data = await resp.json()
    questions.value = data.questions || []
  } catch (e) {
    console.error('Failed to load questions:', e)
  }
})
</script>

<style scoped>
.sample-questions {
  margin-bottom: 20px;
}
.sq-header {
  margin-bottom: 10px;
}
.sq-title {
  font-size: 13px;
  color: #8e99b0;
  font-weight: 600;
  letter-spacing: 0.3px;
}
.sq-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.sq-chip {
  font-size: 13px;
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #e4e9f2;
  border-radius: 20px;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.sq-chip:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: #fff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}
.sq-chip:active {
  transform: translateY(0);
}
</style>
