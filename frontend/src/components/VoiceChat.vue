<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { onBeforeRouteLeave } from 'vue-router'
import { BACKEND_URL } from '../config.js'
import { authHeaders, handleUnauthorized } from '../auth.js'
import { friendlyError } from '../errors.js'

const router = useRouter()

const status = ref('idle')
const errorMessage = ref('')
const messages = ref([])
const language = ref('')
const sessionSeconds = ref(0)
const transcriptEl = ref(null)
const showTranscript = ref(true)
const displayMessages = computed(() => messages.value.filter(m => m.role === 'assistant'))

let peerConnection = null
let dataChannel = null
let audioElement = null
let mediaStream = null
let conversationSaved = false
let timerInterval = null
let assistantMsgIndex = -1
let connectionTimeout = null
let silenceTimeout = null

// --- Preferences ---

onMounted(async () => {
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

// --- Timer ---

function startTimer() {
  sessionSeconds.value = 0
  timerInterval = setInterval(() => {
    sessionSeconds.value++
  }, 1000)
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

function formatTime(totalSeconds) {
  const mins = Math.floor(totalSeconds / 60)
  const secs = totalSeconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// --- Transcript scrolling ---

async function scrollTranscript() {
  await nextTick()
  if (transcriptEl.value) {
    transcriptEl.value.scrollTop = transcriptEl.value.scrollHeight
  }
}

// --- Connection health ---

function startConnectionTimeout() {
  connectionTimeout = setTimeout(() => {
    if (status.value === 'connecting') {
      errorMessage.value = 'Connection timed out. Please check your internet and try again.'
      status.value = 'error'
      stopConversation()
    }
  }, 15000)
}

function clearConnectionTimeout() {
  if (connectionTimeout) {
    clearTimeout(connectionTimeout)
    connectionTimeout = null
  }
}

function startSilenceTimeout() {
  silenceTimeout = setTimeout(() => {
    if (status.value === 'connected') {
      errorMessage.value = 'No response from AI — try reconnecting.'
      status.value = 'error'
      stopConversation()
    }
  }, 15000)
}

function clearSilenceTimeout() {
  if (silenceTimeout) {
    clearTimeout(silenceTimeout)
    silenceTimeout = null
  }
}

// --- Save ---

async function saveConversation() {
  if (localStorage.getItem('isGuest') === 'true') return
  if (messages.value.length === 0 || conversationSaved) return

  try {
    await fetch(`${BACKEND_URL}/api/conversations`, {
      method: 'POST',
      headers: {
        ...authHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        mode: 'voice',
        messages: messages.value,
      }),
    })
    conversationSaved = true
  } catch (err) {
    console.error('Failed to save conversation:', err)
    errorMessage.value = friendlyError(err, 'Your conversation could not be saved.')
    status.value = 'error'
  }
}

// --- Connection ---

async function startConversation() {
  status.value = 'connecting'
  errorMessage.value = ''
  messages.value = []
  conversationSaved = false
  assistantMsgIndex = -1

  try {
    startConnectionTimeout()

    const tokenResponse = await fetch(`${BACKEND_URL}/api/token`, {
      method: 'POST',
      headers: authHeaders(),
    })

    if (tokenResponse.status === 401) {
      handleUnauthorized(router)
      return
    }

    if (!tokenResponse.ok) {
      throw new Error('Failed to get token from backend')
    }

    const tokenData = await tokenResponse.json()
    const ephemeralKey = tokenData.value

    const pc = new RTCPeerConnection()
    peerConnection = pc

    audioElement = document.createElement('audio')
    audioElement.autoplay = true
    pc.ontrack = (event) => {
      audioElement.srcObject = event.streams[0]
    }

    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    pc.addTrack(mediaStream.getTracks()[0])

    dataChannel = pc.createDataChannel('oai-events')

    dataChannel.onopen = () => {
      clearConnectionTimeout()
      status.value = 'connected'
      startTimer()
      startSilenceTimeout()
    }

    dataChannel.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        clearSilenceTimeout()

        // OpenAI error event — surface to user.
        if (msg.type === 'error') {
          console.error('OpenAI error:', msg)
          errorMessage.value = msg.error?.message || 'An error occurred during the conversation.'
          status.value = 'error'
          stopConversation()
          return
        }

        // User transcript — appears as a complete block.
        if (
          msg.type === 'conversation.item.input_audio_transcription.completed'
          && msg.transcript
        ) {
          messages.value.push({ role: 'user', content: msg.transcript })
          scrollTranscript()
        }

        // Assistant transcript — streams word-by-word via deltas.
        if (
          msg.type === 'response.output_audio_transcript.delta'
          && msg.delta
        ) {
          if (assistantMsgIndex === -1) {
            messages.value.push({ role: 'assistant', content: msg.delta })
            assistantMsgIndex = messages.value.length - 1
          } else {
            messages.value[assistantMsgIndex].content += msg.delta
          }
          scrollTranscript()
        }

        // Assistant transcript complete — finalize and reset index.
        if (msg.type === 'response.output_audio_transcript.done') {
          if (assistantMsgIndex !== -1 && msg.transcript) {
            messages.value[assistantMsgIndex].content = msg.transcript
          }
          assistantMsgIndex = -1
          scrollTranscript()
        }
      } catch {
        // Ignore non-JSON or unexpected messages.
      }
    }

    const offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    const sdpResponse = await fetch('https://api.openai.com/v1/realtime/calls', {
      method: 'POST',
      body: offer.sdp,
      headers: {
        Authorization: `Bearer ${ephemeralKey}`,
        'Content-Type': 'application/sdp',
      },
    })

    if (!sdpResponse.ok) {
      throw new Error('Failed to connect to OpenAI Realtime API')
    }

    const answer = {
      type: 'answer',
      sdp: await sdpResponse.text(),
    }
    await pc.setRemoteDescription(answer)

    pc.oniceconnectionstatechange = () => {
      if (pc.iceConnectionState === 'failed' || pc.iceConnectionState === 'disconnected') {
        stopConversation()
      }
    }
  } catch (err) {
    console.error('Connection error:', err)
    errorMessage.value = err.message
    status.value = 'error'
    stopConversation()
  }
}

async function stopConversation() {
  stopTimer()
  clearConnectionTimeout()
  clearSilenceTimeout()
  await saveConversation()

  if (dataChannel) {
    dataChannel.close()
    dataChannel = null
  }

  if (peerConnection) {
    peerConnection.close()
    peerConnection = null
  }

  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop())
    mediaStream = null
  }

  if (audioElement) {
    audioElement.srcObject = null
    audioElement = null
  }

  assistantMsgIndex = -1

  if (status.value !== 'error') {
    status.value = 'idle'
  }
}

onBeforeRouteLeave(async () => {
  await saveConversation()
})

onUnmounted(() => {
  stopTimer()
  stopConversation()
})
</script>

<template>
  <div class="voice-chat">
    <!-- Top bar -->
    <div class="top-bar">
      <span v-if="language" class="lang-badge">{{ language }}</span>
      <span v-if="status === 'connected'" class="timer">{{ formatTime(sessionSeconds) }}</span>
    </div>

    <!-- Center area -->
    <div class="center-area">
      <div class="pulse-ring" :class="status === 'connected' ? 'pulse-active' : 'pulse-idle'">
        <!-- Idle: mic icon -->
        <svg v-if="status !== 'connected'" class="mic-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
          <line x1="12" y1="19" x2="12" y2="23"/>
        </svg>
        <!-- Connected: animated wave bars -->
        <div v-else class="wave-bars">
          <div class="wave-bar wb1"></div>
          <div class="wave-bar wb2"></div>
          <div class="wave-bar wb3"></div>
          <div class="wave-bar wb4"></div>
          <div class="wave-bar wb5"></div>
        </div>
      </div>

      <p class="status-text">
        <span v-if="status === 'idle'">Ready to practice</span>
        <span v-else-if="status === 'connecting'">Connecting...</span>
        <span v-else-if="status === 'connected'">Connected — start speaking!</span>
        <span v-else-if="status === 'error'">{{ errorMessage }}</span>
      </p>

      <button
        v-if="status === 'idle' || status === 'error'"
        @click="startConversation"
        class="btn-start"
      >
        Start conversation
      </button>

      <button v-else-if="status === 'connecting'" disabled class="btn-connecting">
        Connecting...
      </button>

      <button v-else @click="stopConversation" class="btn-stop">
        Stop
      </button>
    </div>

    <!-- Live transcript -->
    <div class="transcript-section">
      <div class="transcript-header">
        <p class="transcript-label">Live transcript</p>
        <button @click="showTranscript = !showTranscript" class="toggle-btn">
          {{ showTranscript ? 'Hide' : 'Show' }}
        </button>
      </div>

      <template v-if="showTranscript">
        <div v-if="displayMessages.length === 0" class="empty-transcript">
          Your conversation will appear here...
        </div>

        <div v-else class="transcript-scroll" ref="transcriptEl">
          <div
            v-for="(msg, index) in displayMessages"
            :key="index"
            class="t-msg t-assistant"
          >
            <p class="t-content">{{ msg.content }}</p>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.voice-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 2rem 2rem;
  max-width: 600px;
  margin: 0 auto;
  border: 1px solid #ddd;
  border-radius: 12px;
}

/* --- Top bar --- */

.top-bar {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #ddd;
}

.lang-badge {
  font-size: 0.8rem;
  font-weight: bold;
  background-color: #e1f5ee;
  color: #0F6E56;
  padding: 0.2rem 0.65rem;
  border-radius: 12px;
}

.timer {
  font-size: 0.85rem;
  color: #999;
  font-variant-numeric: tabular-nums;
}

/* --- Center area --- */

.center-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem 0 2rem;
}

.pulse-ring {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pulse-idle {
  background-color: #252525;
  border: 1px solid #ddd;
}

.pulse-active {
  background-color: #e1f5ee;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(29, 158, 117, 0.25); }
  50% { box-shadow: 0 0 0 18px rgba(29, 158, 117, 0); }
}

.mic-icon {
  color: #999;
}

.wave-bars {
  display: flex;
  gap: 3px;
  align-items: center;
  height: 28px;
}

.wave-bar {
  width: 4px;
  border-radius: 2px;
  background-color: #1D9E75;
}

.wb1 { height: 12px; animation: wb 0.8s ease-in-out infinite; }
.wb2 { height: 20px; animation: wb 0.8s ease-in-out 0.15s infinite; }
.wb3 { height: 16px; animation: wb 0.8s ease-in-out 0.3s infinite; }
.wb4 { height: 24px; animation: wb 0.8s ease-in-out 0.45s infinite; }
.wb5 { height: 14px; animation: wb 0.8s ease-in-out 0.6s infinite; }

@keyframes wb {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.4); }
}

.status-text {
  font-size: 1rem;
  color: #666;
}

button {
  padding: 0.6rem 1.75rem;
  font-size: 1rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 500;
}

.btn-start {
  background-color: #1D9E75;
  color: white;
}

.btn-start:hover {
  background-color: #0F6E56;
}

.btn-stop {
  background-color: #E24B4A;
  color: white;
}

.btn-stop:hover {
  background-color: #A32D2D;
}

.btn-connecting {
  background-color: #888;
  color: white;
  cursor: not-allowed;
}

/* --- Transcript --- */

.transcript-section {
  width: 100%;
}

.transcript-label {
  font-size: 0.75rem;
  font-weight: bold;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 0.5rem;
}

.empty-transcript {
  font-size: 0.85rem;
  color: #bbb;
  text-align: center;
  padding: 1.5rem 0;
}

.transcript-scroll {
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.t-msg {
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  max-width: 85%;
}

.t-user {
  background-color: #e1f5ee;
  align-self: flex-end;
}

.t-assistant {
  background-color: #f5f5f5;
  align-self: flex-start;
}

.t-role {
  font-size: 0.7rem;
  font-weight: bold;
  color: #0F6E56;
  margin-bottom: 0.15rem;
}

.t-assistant .t-role {
  color: #999;
}

.t-content {
  margin: 0;
  font-size: 0.85rem;
  color: #333;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .voice-chat {
    padding: 0 1rem 1rem;
  }

  .center-area {
    padding: 1rem 0 1.5rem;
  }

  .transcript-scroll {
    max-height: 200px;
  }
}

.transcript-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.transcript-header .transcript-label {
  margin: 0;
}

.toggle-btn {
  padding: 0.2rem 0.6rem;
  font-size: 0.75rem;
  background: none;
  border: 1px solid #ccc;
  border-radius: 4px;
  color: #666;
  cursor: pointer;
  font-weight: 400;
}

.toggle-btn:hover {
  border-color: #999;
  color: #333;
}
</style>