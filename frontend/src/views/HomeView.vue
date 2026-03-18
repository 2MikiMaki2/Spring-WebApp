<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <main>
    <h1>Language Practice</h1>
    <p class="subtitle">Choose a practice mode</p>

    <div class="mode-links">
      <RouterLink to="/voice" class="mode-card">
        <span class="mode-title">Voice Chat</span>
        <span class="mode-desc">Practice speaking and listening</span>
      </RouterLink>

      <RouterLink to="/text" class="mode-card">
        <span class="mode-title">Text Chat</span>
        <span class="mode-desc">Practice reading and writing</span>
      </RouterLink>
    </div>
  </main>
</template>

<style scoped>
main {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
}

h1 {
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  margin-bottom: 2rem;
}

.mode-links {
  display: flex;
  gap: 1.5rem;
}

.mode-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 3rem;
  border: 1px solid #ddd;
  border-radius: 12px;
  text-decoration: none;
  color: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.mode-card:hover {
  border-color: #4a9c6d;
  box-shadow: 0 2px 8px rgba(74, 156, 109, 0.15);
}

.mode-title {
  font-size: 1.25rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.mode-desc {
  font-size: 0.9rem;
  color: #888;
}
</style>