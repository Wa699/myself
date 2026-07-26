<template>
  <div class="sample-questions">
    <h3 class="sq-title">试试这些问题</h3>
    <div class="sq-list">
      <button v-for="q in questions" :key="q" class="sq-chip" @click="$emit('select', q)">{{ q }}</button>
    </div>
  </div>
</template>

<script setup>
defineEmits(['select'])
const questions = [
  '张三有哪些核心技术能力？',
  '请介绍一下张三做的电商平台微服务改造项目',
  '张三的教育背景是什么？',
  '张三获得过哪些荣誉？',
  '张三会哪些编程语言？'
]
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
