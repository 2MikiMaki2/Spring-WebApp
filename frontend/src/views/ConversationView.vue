<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const BACKEND_URL = 'https://backend-production-2cd9.up.railway.app'
const router = useRouter()
const route = useRoute()

const conversation = ref(null)
const isLoading = ref(true)
const isDeleting = ref(false)
const errorMessage = ref('')

function authHeaders() {
  return { Authorization: `Bearer ${localStorage.getItem('token')}` }
}

onMounted(async () => {
  try {
    const response = await fetch(
      `${BACKEND_URL}/api/conversations/${route.params.id}`,
      { headers: authHeaders() },
    )

    if (response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userName')
      router.push('/login')
      return
    }

    if (response.status === 404) {
      errorMessage.value = 'Conversation not found.'
      return
    }

    if (!response.ok) {
      throw new Error('Failed to load conversation')
    }

    const data = await response.json()
    conversation.value = data.conversation
  } catch (err) {
    console.error('Failed to load conversation:', err)
    errorMessage.value = 'Something went wrong. Please try again.'
  } finally {
    isLoading.value = false
  }
})

async function deleteConversation() {
  if (!confirm('Delete this conversation? This cannot be undone.')) return

  isDeleting.value = true

  try {
    const response = await fetch(
      `${BACKEND_URL}/api/conversations/${route.params.id}`,
      { method: 'DELETE', headers: authHeaders() },
    )

    if (response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userName')
      router.push('/login')
      return
    }

    if (!response.ok) {
      throw new Error('Failed to delete conversation')
    }

    router.push('/history')
  } catch (err) {
    console.error('Delete error:', err)
    errorMessage.value = 'Failed to delete. Please try again.'
    isDeleting.value = false
  }
}

function formatDate(isoString) {
  const date = new Date(isoString)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <main>
    <router-link to="/history" class="back-link">&larr; Back to history</router-link>

    <div v-if="isLoading" class="loading">Loading conversation...</div>

    <div v-else-if="errorMessage" class="error">{{ errorMessage }}</div>

    <template v-else-if="conversation">
      <div class="conversation-header">
        <div class="header-left">
          <span class="mode-badge" :class="conversation.mode">{{ conversation.mode }}</span>
          <span class="date">{{ formatDate(conversation.created_at) }}</span>
        </div>
        <button
          @click="deleteConversation"
          :disabled="isDeleting"
          class="delete-btn"
        >
          {{ isDeleting ? 'Deleting...' : 'Delete' }}
        </button>
      </div>

      <div class="message-list">
        <div
          v-for="(msg, index) in conversation.messages"
          :key="index"
          class="message"
          :class="msg.role"
        >
          <span class="label">{{ msg.role === 'user' ? 'You' : 'Assistant' }}</span>
          <p class="content">{{ msg.content }}</p>
        </div>
      </div>
    </template>
  </main>
</template>

<style scoped>
main {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
}

.back-link {
  align-self: flex-start;
  margin-bottom: 1rem;
  text-decoration: none;
  color: #4a9c6d;
  font-size: 0.9rem;
}

.back-link:hover {
  text-decoration: underline;
}

.loading,
.error {
  color: #888;
}

.conversation-header {
  width: 100%;
  max-width: 600px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
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
  font-size: 0.85rem;
  color: #999;
}

.delete-btn {
  padding: 0.35rem 0.9rem;
  font-size: 0.85rem;
  background: none;
  border: 1px solid #ccc;
  border-radius: 4px;
  color: #c44b4b;
  cursor: pointer;
}

.delete-btn:hover:not(:disabled) {
  border-color: #c44b4b;
  background-color: #c44b4b;
  color: white;
}

.delete-btn:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.message-list {
  width: 100%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  padding: 0.75rem 1rem;
  border-radius: 8px;
}

.message.user {
  background-color: #e8f5e9;
  align-self: flex-end;
}

.message.assistant {
  background-color: #f5f5f5;
  align-self: flex-start;
}

.label {
  font-size: 0.75rem;
  font-weight: bold;
  color: #888;
  display: block;
  margin-bottom: 0.25rem;
}

.content {
  margin: 0;
  color: #333;
  line-height: 1.5;
}
</style>