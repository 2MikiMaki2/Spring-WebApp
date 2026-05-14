<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { onBeforeRouteLeave } from 'vue-router'
import { authHeaders, handleUnauthorized } from '../auth.js'
import { BACKEND_URL } from '../config.js'
import { friendlyError } from '../errors.js'

const router = useRouter()

const messages = ref([])
const userInput = ref('')
const isLoading = ref(false)
const messageListEl = ref(null)
const language = ref('')
const userInitial = ref('')
const saveError = ref('')

let conversationSaved = false

// --- Preferences & user info ---

onMounted(async () => {
  const name = localStorage.getItem('userName') || ''
  userInitial.value = name.charAt(0).toUpperCase()

  try {
    const response = await fetch(`${BACKEND_URL}/api/preferences`, {
      headers: authHeaders(),
    })
    if (response.status === 401) {
      handleUnauthorized(router)
      return
    }
    if (response.ok) {
      const data = await response.json()
      language.value = data.preferences.target_language
    }
  } catch (err) {
    console.error('Failed to load preferences:', err)
  }
})

// --- Save ---

async function saveConversation() {
  if (messages.value.length === 0 || conversationSaved) return

  try {
    await fetch(`${BACKEND_URL}/api/conversations`, {
      method: 'POST',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mode: 'text',
        messages: messages.value,
      }),
    })
    conversationSaved = true
  } catch (err) {
    console.error('Failed to save conversation:', err)
    saveError.value = friendlyError(err, 'Your conversation could not be saved.')
  }
}

async function newChat() {
  await saveConversation()
  messages.value = []
  conversationSaved = false
  saveError.value = ''
}

onBeforeRouteLeave(async () => {
  await saveConversation()
})

// --- Send ---

async function sendMessage() {
  const text = userInput.value.trim()
  if (!text || isLoading.value) return

  messages.value.push({ role: 'user', content: text })
  userInput.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: 'POST',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: messages.value }),
    })

    if (response.status === 401) {
      handleUnauthorized(router)
      return
    }

    if (!response.ok) {
      throw new Error('Failed to get response')
    }

    const data = await response.json()
    messages.value.push({ role: 'assistant', content: data.reply })
  } catch (err) {
    console.error('Chat error:', err)
    messages.value.push({
      role: 'assistant',
      content: 'Sorry, something went wrong. Please try again.',
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

function handleKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

async function scrollToBottom() {
  await nextTick()
  if (messageListEl.value) {
    messageListEl.value.scrollTop = messageListEl.value.scrollHeight
  }
}
</script>

<template>
  <div class="text-chat">
    <!-- Top bar -->
    <div class="top-bar">
      <span v-if="language" class="lang-badge">{{ language }}</span>
      <button
        @click="newChat"
        :disabled="messages.length === 0 || isLoading"
        class="new-chat-btn"
      >
        New chat
      </button>
    </div>

    <!-- Save warning -->
    <p v-if="saveError" class="save-error">{{ saveError }}</p>

    <!-- Messages -->
    <div class="message-list" ref="messageListEl">
      <div v-if="messages.length === 0" class="empty-state">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.2" stroke-linecap="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <p>Say something!</p>
      </div>

      <template v-else>
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="msg-row"
          :class="msg.role === 'user' ? 'msg-row-user' : 'msg-row-assistant'"
        >
          <div class="avatar" :class="msg.role === 'user' ? 'avatar-user' : 'avatar-ai'">
            {{ msg.role === 'user' ? userInitial : 'AI' }}
          </div>
          <div class="bubble" :class="msg.role === 'user' ? 'bubble-user' : 'bubble-ai'">
            {{ msg.content }}
          </div>
        </div>

        <!-- Typing indicator -->
        <div v-if="isLoading" class="msg-row msg-row-assistant">
          <div class="avatar avatar-ai">AI</div>
          <div class="bubble bubble-ai typing-bubble">
            <div class="typing-dots">
              <span class="dot dot1"></span>
              <span class="dot dot2"></span>
              <span class="dot dot3"></span>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- Input -->
    <div class="input-area">
      <textarea
        v-model="userInput"
        @keydown="handleKeydown"
        placeholder="Type a message..."
        rows="1"
        :disabled="isLoading"
      ></textarea>
      <button
        @click="sendMessage"
        :disabled="isLoading || !userInput.trim()"
        class="send-btn"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"/>
          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.text-chat {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 600px;
  height: 520px;
  margin: 0 auto;
}

/* --- Top bar --- */

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
}

.lang-badge {
  font-size: 0.8rem;
  font-weight: bold;
  background-color: #e6f1fb;
  color: #185FA5;
  padding: 0.2rem 0.65rem;
  border-radius: 12px;
}

.new-chat-btn {
  padding: 0.2rem 0.6rem;
  font-size: 0.8rem;
  background: none;
  border: 1px solid #ccc;
  border-radius: 4px;
  color: #666;
  cursor: pointer;
}

.new-chat-btn:hover:not(:disabled) {
  border-color: #999;
  color: #333;
}

.new-chat-btn:disabled {
  color: #ccc;
  border-color: #eee;
  cursor: not-allowed;
}

/* --- Messages --- */

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 12px 12px 0 0;
  background: #1a1a1a;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.empty-state p {
  font-size: 0.85rem;
  color: #bbb;
  text-align: center;
}

.msg-row {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}

.msg-row-user {
  flex-direction: row-reverse;
}

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: bold;
  flex-shrink: 0;
}

.avatar-user {
  background-color: #e1f5ee;
  color: #0F6E56;
}

.avatar-ai {
  background-color: #e6f1fb;
  color: #185FA5;
}

.bubble {
  padding: 0.5rem 0.75rem;
  border-radius: 12px;
  font-size: 0.9rem;
  line-height: 1.5;
  max-width: 75%;
  color: #333;
}

.bubble-user {
  background-color: #e1f5ee;
  border-bottom-right-radius: 4px;
}

.bubble-ai {
  background-color: #f0f0f0;
  border-bottom-left-radius: 4px;
}

/* --- Typing indicator --- */

.typing-bubble {
  padding: 0.65rem 0.85rem;
}

.typing-dots {
  display: flex;
  gap: 4px;
  align-items: center;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #888;
}

.dot1 { animation: bounce 1.2s ease-in-out infinite; }
.dot2 { animation: bounce 1.2s ease-in-out 0.2s infinite; }
.dot3 { animation: bounce 1.2s ease-in-out 0.4s infinite; }

@keyframes bounce {
  0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
  30% { opacity: 1; transform: translateY(-3px); }
}

/* --- Input --- */

.input-area {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
  padding: 0.65rem;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 12px 12px;
  background: #1a1a1a;
}

.input-area textarea {
  flex: 1;
  resize: none;
  padding: 0.5rem 0.75rem;
  font-size: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: inherit;
  line-height: 1.4;
  background: #fff;
  color: #333;
}

.input-area textarea:focus {
  outline: none;
  border-color: #1D9E75;
}

.send-btn {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  border: none;
  background-color: #1D9E75;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background-color: #0F6E56;
}

.send-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .text-chat {
    height: calc(100vh - 120px);
    max-width: 100%;
  }
}

.save-error {
  color: #c44b4b;
  font-size: 0.8rem;
  text-align: center;
  padding: 0.4rem;
  margin: 0;
}
</style>