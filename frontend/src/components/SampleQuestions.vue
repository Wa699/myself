<template>
  <div class="sample-questions" v-if="questions.length">
    <h3 class="sq-title">试试这些问题</h3>
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
.sample-questions { margin-bottom: 16px; }
.sq-title { font-size: 14px; color: #888; margin-bottom: 8px; font-weight: 500; }
.sq-list { display: flex; flex-wrap: wrap; gap: 8px; }
.sq-chip {
  font-size: 13px;
  padding: 6px 14px;
  background: #fff;
  border: 1px solid #dde4f0;
  border-radius: 16px;
  color: #4a6cf7;
  cursor: pointer;
  transition: all 0.15s;
}
.sq-chip:hover { background: #f0f4ff; border-color: #4a6cf7; }
</style>