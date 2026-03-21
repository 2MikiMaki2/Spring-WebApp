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
      No conversations yet. Start a voice or text session to see your history here.
    </div>

    <div v-else class="conversation-list">
      <router-link
        v-for="conv in conversations"
        :key="conv.id"
        :to="`/history/${conv.id}`"
        class="conversation-card"
      >
        <div class="card-header">
          <span class="mode-badge" :class="conv.mode">{{ conv.mode }}</span>
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
  padding: 2rem;
}

h1 {
  margin-bottom: 1.5rem;
}

.loading,
.empty-state {
  color: #888;
}

.conversation-list {
  width: 100%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.conversation-card {
  display: block;
  padding: 1rem 1.25rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.conversation-card:hover {
  border-color: #4a9c6d;
  box-shadow: 0 2px 8px rgba(74, 156, 109, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.mode-badge {
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.mode-badge.voice {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.mode-badge.text {
  background-color: #e3f2fd;
  color: #1565c0;
}

.date {
  font-size: 0.8rem;
  color: #999;
}

.preview {
  font-size: 0.9rem;
  color: #555;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>