<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { BACKEND_URL } from '../config.js'
import { authHeaders, handleUnauthorized } from '../auth.js'

const router = useRouter()
const userName = ref(localStorage.getItem('userName') || '')
const recentConversations = ref([])

onMounted(async () => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/conversations`, {
      headers: authHeaders(),
    })

    if (response.status === 401) {
      handleUnauthorized(router)
      return
    }

    const data = await response.json()
    // Show only the 3 most recent.
    recentConversations.value = data.conversations.slice(0, 3)
  } catch (err) {
    console.error('Failed to load recent conversations:', err)
  }
})

function formatRelativeDate(isoString) {
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays === 1) return 'yesterday'

  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}
</script>

<template>
  <main>
    <h1>Bonjour, {{ userName }}</h1>
    <p class="subtitle">Ready to practice? Pick a mode to get started.</p>

    <div class="mode-links">
      <RouterLink to="/voice" class="mode-card">
        <div class="mode-icon voice-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0F6E56" stroke-width="2" stroke-linecap="round">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/>
          </svg>
        </div>
        <span class="mode-title">Voice chat</span>
        <span class="mode-desc">Speak and listen in real time</span>
      </RouterLink>

      <RouterLink to="/text" class="mode-card">
        <div class="mode-icon text-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#185FA5" stroke-width="2" stroke-linecap="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        <span class="mode-title">Text chat</span>
        <span class="mode-desc">Practice reading and writing</span>
      </RouterLink>
    </div>

    <div v-if="recentConversations.length > 0" class="recent-section">
      <p class="recent-heading">Recent conversations</p>

      <div class="recent-list">
        <RouterLink
          v-for="conv in recentConversations"
          :key="conv.id"
          :to="`/history/${conv.id}`"
          class="recent-item"
        >
          <div class="recent-left">
            <span class="mode-badge" :class="conv.mode">{{ conv.mode }}</span>
            <span class="recent-preview">{{ conv.preview || 'No preview available' }}</span>
          </div>
          <span class="recent-date">{{ formatRelativeDate(conv.created_at) }}</span>
        </RouterLink>
      </div>

      <RouterLink to="/history" class="view-all-link">View all history</RouterLink>
    </div>
  </main>
</template>

<style scoped>
main {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem 2rem 2rem;
}

h1 {
  font-size: 1.75rem;
  margin: 0 0 0.25rem;
}

.subtitle {
  color: #666;
  margin: 0 0 2.5rem;
}

.mode-links {
  display: flex;
  gap: 1rem;
  margin-bottom: 2.5rem;
}

.mode-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem 2.5rem;
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

.mode-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}

.voice-icon {
  background-color: #e1f5ee;
}

.text-icon {
  background-color: #e6f1fb;
}

.mode-title {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.mode-desc {
  font-size: 0.85rem;
  color: #888;
}

.recent-section {
  width: 100%;
  max-width: 480px;
}

.recent-heading {
  font-size: 0.85rem;
  font-weight: bold;
  color: #888;
  margin: 0 0 0.6rem;
}

.recent-list {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0.85rem;
  text-decoration: none;
  color: inherit;
  transition: background-color 0.15s;
}

.recent-item:not(:last-child) {
  border-bottom: 1px solid #eee;
}

.recent-item:hover {
  background-color: #f9f9f9;
}

.recent-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  overflow: hidden;
}

.mode-badge {
  font-size: 0.7rem;
  font-weight: bold;
  text-transform: uppercase;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  flex-shrink: 0;
}

.mode-badge.voice {
  background-color: #e1f5ee;
  color: #0F6E56;
}

.mode-badge.text {
  background-color: #e6f1fb;
  color: #185FA5;
}

.recent-preview {
  font-size: 0.85rem;
  color: #555;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-date {
  font-size: 0.75rem;
  color: #999;
  flex-shrink: 0;
  margin-left: 0.75rem;
}

.view-all-link {
  display: inline-block;
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #1D9E75;
  text-decoration: none;
}

.view-all-link:hover {
  text-decoration: underline;
}
</style>