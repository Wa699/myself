<template>
  <div class="profile-card">
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
const profile = {
  name: '张三',
  title: '高级后端工程师',
  summary: '8年Java后端开发经验，擅长微服务架构设计和性能优化。主导过日活百万级电商平台的后端架构升级。',
  skills: ['Java', 'Spring Boot', 'Spring Cloud', 'MySQL', 'Redis', 'Kafka', 'Docker', 'Kubernetes', 'Python', 'Go']
}
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
