<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authHeaders, handleUnauthorized } from '../auth.js'
import { formatDate } from '../utils.js'
import { BACKEND_URL } from '../config.js'

const router = useRouter()

const conversations = ref([])
const isLoading = ref(true)

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
    conversations.value = data.conversations
  } catch (err) {
    console.error('Failed to load conversations:', err)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <main>
    <h1>Conversation History</h1>

    <div v-if="isLoading" class="loading">Loading conversations...</div>

    <div v-else-if="conversations.length === 0" class="empty-state">
    <p>No conversations yet!</p>
    <p>Start a <router-link to="/voice">voice</router-link> or <router-link to="/text">text</router-link> session — your conversations will appear here.</p>
    </div>

    <div v-else class="conversation-list">
      <router-link
        v-for="conv in conversations"
        :key="conv.id"
        :to="`/history/${conv.id}`"
        class="conversation-card"
      >
        <div class="card-header">
          <span class="fc-badge" :class="conv.mode">{{ conv.mode }}</span>
          <span class="date">{{ formatDate(conv.created_at) }}</span>
        </div>
        <p class="preview">{{ conv.preview || 'No preview available' }}</p>
      </router-link>
    </div>
  </main>
</template>

<style scoped>
main {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: clamp(1.5rem, 4vw, 2.5rem) 0;
}

h1 {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(2rem, 4.5vw, 2.6rem);
  color: var(--text-strong);
  margin-bottom: 1.5rem;
}

.loading,
.empty-state {
  color: var(--text-muted);
}

.conversation-list {
  width: 100%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.conversation-card {
  display: block;
  padding: 1.1rem 1.3rem;
  background: var(--surface-raised);
  border: 1px solid var(--border);
  border-radius: var(--radius-panel);
  box-shadow: var(--shadow-rest);
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.conversation-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.date {
  font-size: 0.86rem;
  color: var(--text-faint);
}

.preview {
  font-size: 0.92rem;
  color: var(--text-body);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>