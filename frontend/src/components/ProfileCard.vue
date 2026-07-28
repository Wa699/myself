<template>
  <div class="profile-card" v-if="profile.name">
    <div class="profile-accent"></div>
    <div class="profile-body">
      <div class="profile-header">
        <div class="profile-avatar">
          {{ profile.name.charAt(0) }}
        </div>
        <div class="profile-meta">
          <h2 class="profile-name">{{ profile.name }}</h2>
          <span class="profile-title">{{ profile.title }}</span>
        </div>
      </div>
      <p class="profile-summary">{{ profile.summary }}</p>
      <div class="skill-tags">
        <span v-for="skill in profile.skills" :key="skill" class="skill-tag">{{ skill }}</span>
      </div>
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
  border-radius: 12px;
  margin-bottom: 20px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.3s;
}
.profile-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
.profile-accent {
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}
.profile-body {
  padding: 20px 24px;
}
.profile-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 12px;
}
.profile-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
}
.profile-meta {
  min-width: 0;
}
.profile-name {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
  line-height: 1.3;
}
.profile-title {
  font-size: 13px;
  color: #667eea;
  background: #f0f3ff;
  padding: 3px 12px;
  border-radius: 20px;
  display: inline-block;
  margin-top: 2px;
  font-weight: 500;
}
.profile-summary {
  font-size: 14px;
  color: #5a6278;
  line-height: 1.7;
  margin-bottom: 14px;
}
.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.skill-tag {
  font-size: 12px;
  padding: 5px 12px;
  background: linear-gradient(135deg, #f7f8ff 0%, #eef1ff 100%);
  color: #5b6ce8;
  border-radius: 20px;
  font-weight: 500;
  border: 1px solid #e8ebff;
  transition: all 0.2s;
}
.skill-tag:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-color: transparent;
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(102, 126, 234, 0.25);
}
</style>
