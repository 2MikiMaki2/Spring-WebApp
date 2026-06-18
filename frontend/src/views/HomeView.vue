<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { BACKEND_URL } from '../config.js'
import { authHeaders, handleUnauthorized } from '../auth.js'
import { friendlyError } from '../errors.js'

const router = useRouter()
const userName = ref(localStorage.getItem('userName') || '')
const recentConversations = ref([])
const greeting = ref('Hello')
const loadError = ref('')
const isGuest = localStorage.getItem('isGuest') === 'true'

onMounted(async () => {
  try {
    const prefsResponse = await fetch(`${BACKEND_URL}/api/preferences`, {
      headers: authHeaders(),
    })
    if (prefsResponse.ok) {
      const prefsData = await prefsResponse.json()
      greeting.value = prefsData.preferences.greeting
    }
  } catch (err) {
    console.error('Failed to load preferences:', err)
  }

  if (!isGuest) {
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
      loadError.value = friendlyError(err, 'Could not load recent conversations.')
    }
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
    <h1 class="greeting">{{ greeting }}, {{ userName }}</h1>
    <p class="subtitle">Ready to practice? Pick a mode to get started.</p>

    <div class="mode-links">
      <RouterLink to="/voice" class="mode-card mode-card-voice">
        <div class="mode-icon voice-icon">
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/>
          </svg>
        </div>
        <span class="mode-title">Voice chat</span>
        <span class="mode-desc">Speak and listen in real time</span>
      </RouterLink>

      <RouterLink to="/text" class="mode-card mode-card-text">
        <div class="mode-icon text-icon">
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        <span class="mode-title">Text chat</span>
        <span class="mode-desc">Practice reading and writing</span>
      </RouterLink>
    </div>

    <div v-if="!isGuest" class="recent-section">
      <p class="fc-section-label recent-heading">Recent conversations</p>

      <p v-if="loadError" class="fc-error">{{ loadError }}</p>
      <template v-if="recentConversations.length > 0">
      <div class="recent-list">
        <RouterLink
          v-for="conv in recentConversations"
          :key="conv.id"
          :to="`/history/${conv.id}`"
          class="recent-item"
        >
          <div class="recent-left">
            <span class="fc-badge" :class="conv.mode">{{ conv.mode }}</span>
            <span class="recent-preview">{{ conv.preview || 'No preview available' }}</span>
          </div>
          <span class="recent-date">{{ formatRelativeDate(conv.created_at) }}</span>
        </RouterLink>
      </div>
      <RouterLink to="/history" class="view-all-link">View all history <span class="arrow">&rarr;</span></RouterLink>
      </template>
      <p v-else class="empty-recent">Your recent conversations will show up here.</p>
    </div>
  </main>
</template>

<style scoped>
main {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: clamp(2rem, 6vw, 3.5rem) 0 2rem;
}

.greeting {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(2.4rem, 5.6vw, 3.6rem);
  line-height: 1.1;
  color: var(--text-strong);
  margin: 0 0 0.4rem;
  text-align: center;
}

.subtitle {
  font-size: clamp(1rem, 1.7vw, 1.18rem);
  color: var(--text-muted);
  margin: 0 0 2.5rem;
  text-align: center;
}

.mode-links {
  width: 100%;
  max-width: 820px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: clamp(16px, 2.4vw, 24px);
  margin-bottom: 3rem;
}

.mode-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: clamp(30px, 4vw, 42px) 28px;
  background: var(--surface-raised);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-rest);
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.mode-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-hover);
}

.mode-card-voice:hover {
  border-color: var(--brand-tint-2);
}

.mode-card-text:hover {
  border-color: var(--accent-tint-2);
}

.mode-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.9rem;
}

.voice-icon {
  background-color: var(--brand-tint);
  color: var(--brand);
  animation: fc-pulse 2.6s ease-out infinite;
}

.text-icon {
  background-color: var(--accent-tint);
  color: var(--accent-deep);
}

.mode-title {
  font-size: 1.32rem;
  font-weight: 700;
  color: var(--text-strong);
  margin-bottom: 0.35rem;
}

.mode-desc {
  font-size: 0.98rem;
  color: var(--text-muted);
}

.recent-section {
  width: 100%;
  max-width: 780px;
}

.recent-heading {
  margin: 0 0 0.7rem;
}

.recent-list {
  background: var(--surface-raised);
  border: 1px solid var(--border);
  border-radius: var(--radius-panel);
  box-shadow: var(--shadow-rest);
  overflow: hidden;
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.85rem 1.1rem;
  text-decoration: none;
  color: inherit;
  transition: background-color 0.15s ease;
}

.recent-item:not(:last-child) {
  border-bottom: 1px solid var(--border-soft);
}

.recent-item:hover {
  background-color: var(--surface-hover);
}

.recent-left {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  overflow: hidden;
}

.recent-preview {
  font-size: 0.9rem;
  color: var(--text-body);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-date {
  font-size: 0.8rem;
  color: var(--text-faint);
  flex-shrink: 0;
  margin-left: 0.75rem;
}

.view-all-link {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin-top: 0.85rem;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--brand);
}

.view-all-link:hover {
  color: var(--brand-deep);
}

.view-all-link .arrow {
  transition: transform 0.18s ease;
}

.view-all-link:hover .arrow {
  transform: translateX(4px);
}

.empty-recent {
  font-size: 0.9rem;
  color: var(--text-muted);
}
</style>