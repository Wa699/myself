<template>
  <div class="profile-card" v-if="profile.name">
    <div class="profile-header">
      <h2 class="profile-name">{{ profile.name }}</h2>
      <span class="profile-title">{{ profile.title }}</span>
    </div>
    <p class="profile-summary">{{ profile.summary }}</p>
    <div class="skill-tags">
      <span v-for="skill in profile.skills" :key="skill" class="skill-tag">{{ skill }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const profile = ref({ name: '', title: '', summary: '', skills: [] })

onMounted(async () => {
  try {
    const resp = await fetch('/api/profile')
    profile.value = await resp.json()
  } catch (e) {
    console.error('Failed to load profile:', e)
  }
})
</script>

<style scoped>
.profile-card {
  background: #fff;
  border: 1px solid #e8ecf1;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}
.profile-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 10px;
}
.profile-name { font-size: 18px; font-weight: 600; }
.profile-title { font-size: 13px; color: #666; background: #f0f4ff; padding: 2px 10px; border-radius: 4px; }
.profile-summary { font-size: 14px; color: #555; line-height: 1.6; margin-bottom: 12px; }
.skill-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.skill-tag { font-size: 12px; padding: 3px 10px; background: #eef2ff; color: #4a6cf7; border-radius: 4px; }
</style>