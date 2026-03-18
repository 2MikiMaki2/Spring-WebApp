<script setup>
import { ref, nextTick } from 'vue'

const BACKEND_URL = 'https://backend-production-2cd9.up.railway.app'

// The conversation history — an array of { role, content } objects.
// This grows as the user and assistant exchange messages, and the
// entire array is sent to the backend on every request so OpenAI
// has full context of the conversation.
const messages = ref([])
const userInput = ref('')
const isLoading = ref(false)
const messageListEl = ref(null)

async function sendMessage() {
  const text = userInput.value.trim()
  if (!text || isLoading.value) return

  // Add the user's message to the conversation history.
  messages.value.push({ role: 'user', content: text })
  userInput.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: messages.value }),
    })

    if (!response.ok) {
      throw new Error('Failed to get response')
    }

    const data = await response.json()

    // Add the assistant's reply to the conversation history.
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
  // Send on Enter, but allow Shift+Enter for newlines.
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

async function scrollToBottom() {
  // nextTick waits for Vue to finish updating the DOM after a state
  // change, so the new message element exists before we scroll to it.
  await nextTick()
  if (messageListEl.value) {
    messageListEl.value.scrollTop = messageListEl.value.scrollHeight
  }
}
</script>

<template>
  <div class="text-chat">
    <div class="message-list" ref="messageListEl">
      <p v-if="messages.length === 0" class="empty-state">
        Type a message to start practicing...
      </p>

      <div
        v-for="(msg, index) in messages"
        :key="index"
        class="message"
        :class="msg.role"
      >
        <span class="label">{{ msg.role === 'user' ? 'You' : 'AI' }}</span>
        <p class="content">{{ msg.content }}</p>
      </div>

      <div v-if="isLoading" class="message assistant">
        <span class="label">AI</span>
        <p class="content typing">Typing...</p>
      </div>
    </div>

    <div class="input-area">
      <textarea
        v-model="userInput"
        @keydown="handleKeydown"
        placeholder="Type your message..."
        rows="2"
        :disabled="isLoading"
      />
      <button @click="sendMessage" :disabled="isLoading || !userInput.trim()">
        Send
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
  height: 500px;
  color: #333;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px 8px 0 0;
  background: #fafafa;
}

.empty-state {
  color: #999;
  text-align: center;
  margin-top: 2rem;
}

.message {
  margin-bottom: 1rem;
}

.message .label {
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
  color: #888;
}

.message.user .content {
  background: #e3f2fd;
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  margin-top: 0.25rem;
}

.message.assistant .content {
  background: #f0f0f0;
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  margin-top: 0.25rem;
}

.typing {
  color: #999;
  font-style: italic;
}

.input-area {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 8px 8px;
  background: white;
}

.input-area textarea {
  flex: 1;
  resize: none;
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-family: inherit;
}

.input-area button {
  padding: 0.5rem 1.5rem;
  font-size: 1rem;
  background-color: #4a9c6d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.input-area button:hover:not(:disabled) {
  background-color: #3d8259;
}

.input-area button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>