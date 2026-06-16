<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authHeaders, handleUnauthorized } from '../auth.js'
import { formatDate } from '../utils.js'
import { BACKEND_URL } from '../config.js'

const router = useRouter()
const route = useRoute()

const conversation = ref(null)
const isLoading = ref(true)
const isDeleting = ref(false)
const errorMessage = ref('')

onMounted(async () => {
  try {
    const response = await fetch(
      `${BACKEND_URL}/api/conversations/${route.params.id}`,
      { headers: authHeaders() },
    )

    if (response.status === 401) {
      handleUnauthorized(router)
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
      handleUnauthorized(router)
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
</script>

<template>
  <main>
    <router-link to="/history" class="back-link">&larr; Back to history</router-link>

    <div v-if="isLoading" class="loading">Loading conversation...</div>

    <div v-else-if="errorMessage" class="fc-error">{{ errorMessage }}</div>

    <template v-else-if="conversation">
      <div class="conversation-header">
        <div class="header-left">
          <span class="fc-badge" :class="conversation.mode">{{ conversation.mode }}</span>
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
  color: var(--brand);
  font-weight: 600;
  font-size: 0.9rem;
}

.back-link:hover {
  color: var(--brand-deep);
}

.loading {
  color: var(--text-muted);
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

.date {
  font-size: 0.86rem;
  color: var(--text-faint);
}

.delete-btn {
  padding: 0.4rem 1rem;
  font-size: 0.85rem;
  font-weight: 500;
  background: none;
  border: 1.5px solid var(--border-control);
  border-radius: var(--radius-control);
  color: var(--danger);
  cursor: pointer;
  transition: border-color 0.15s ease, background-color 0.15s ease, color 0.15s ease;
}

.delete-btn:hover:not(:disabled) {
  border-color: var(--danger);
  background-color: var(--danger);
  color: white;
}

.delete-btn:disabled {
  color: var(--border-control);
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
  padding: 0.8rem 1.05rem;
  border-radius: var(--radius-control);
  max-width: 85%;
}

.message.user {
  background-color: var(--brand-tint);
  align-self: flex-end;
}

.message.assistant {
  background-color: var(--accent-tint);
  align-self: flex-start;
}

.label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-muted);
  display: block;
  margin-bottom: 0.25rem;
}

.content {
  margin: 0;
  color: var(--text-strong);
  line-height: 1.5;
}

@media (max-width: 768px) {
  main {
    padding: 1rem;
  }

  .conversation-header {
    max-width: 100%;
  }

  .message-list {
    max-width: 100%;
  }
}
</style>