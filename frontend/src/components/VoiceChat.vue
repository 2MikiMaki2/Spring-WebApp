<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { onBeforeRouteLeave } from 'vue-router'

const BACKEND_URL = 'https://backend-production-2cd9.up.railway.app'
const router = useRouter()

const status = ref('idle')
const errorMessage = ref('')
const messages = ref([])

let peerConnection = null
let dataChannel = null
let audioElement = null
let mediaStream = null
let conversationSaved = false

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('token')}`,
  }
}

async function saveConversation() {
  if (messages.value.length === 0 || conversationSaved) return

  try {
    await fetch(`${BACKEND_URL}/api/conversations`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({
        mode: 'voice',
        messages: messages.value,
      }),
    })
    conversationSaved = true
  } catch (err) {
    console.error('Failed to save conversation:', err)
  }
}

async function startConversation() {
  status.value = 'connecting'
  errorMessage.value = ''

  // Reset transcript state for a new conversation.
  messages.value = []
  conversationSaved = false

  try {
    // Step 1: Get an ephemeral token from our backend.
    const token = localStorage.getItem('token')
    const tokenResponse = await fetch(`${BACKEND_URL}/api/token`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (tokenResponse.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userName')
      router.push('/login')
      return
    }

    if (!tokenResponse.ok) {
      throw new Error('Failed to get token from backend')
    }

    const tokenData = await tokenResponse.json()
    const ephemeralKey = tokenData.value

    // Step 2: Create a WebRTC peer connection.
    const pc = new RTCPeerConnection()
    peerConnection = pc

    // Step 3: Set up audio playback.
    audioElement = document.createElement('audio')
    audioElement.autoplay = true
    pc.ontrack = (event) => {
      audioElement.srcObject = event.streams[0]
    }

    // Step 4: Capture the user's microphone.
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    pc.addTrack(mediaStream.getTracks()[0])

    // Step 5: Create a data channel for control events.
    dataChannel = pc.createDataChannel('oai-events')

    dataChannel.onopen = () => {
      status.value = 'connected'

      // Enable transcription of the user's speech so we can save it.
      dataChannel.send(JSON.stringify({
        type: 'session.update',
        session: {
          input_audio_transcription: {
            model: 'whisper-1',
          },
        },
      }))
    }

    dataChannel.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)

        if (
          msg.type === 'conversation.item.input_audio_transcription.completed'
          && msg.transcript
        ) {
          messages.value.push({ role: 'user', content: msg.transcript })
        }

        if (
          msg.type === 'response.output_audio_transcript.done'
          && msg.transcript
        ) {
          messages.value.push({ role: 'assistant', content: msg.transcript })
        }
      } catch {
        // Ignore non-JSON or unexpected messages.
      }
    }

    // Step 6: SDP handshake with OpenAI.
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

  if (status.value !== 'error') {
    status.value = 'idle'
  }
}

// Save the conversation automatically when the user navigates away.
onBeforeRouteLeave(async () => {
  await saveConversation()
})

onUnmounted(() => {
  stopConversation()
})
</script>

<template>
  <div class="voice-chat">
    <p class="status-text">
      <span v-if="status === 'idle'">Ready to practice</span>
      <span v-else-if="status === 'connecting'">Connecting...</span>
      <span v-else-if="status === 'connected'">Connected — start speaking!</span>
      <span v-else-if="status === 'error'">{{ errorMessage }}</span>
    </p>

    <button
      v-if="status === 'idle' || status === 'error'"
      @click="startConversation"
      class="start-btn"
    >
      Start conversation
    </button>

    <button v-else-if="status === 'connecting'" disabled class="connecting-btn">
      Connecting...
    </button>

    <button v-else @click="stopConversation" class="stop-btn">Stop</button>
  </div>
</template>

<style scoped>
.voice-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  padding: 2rem;
}

.status-text {
  font-size: 1.1rem;
  color: #666;
}

button {
  padding: 0.75rem 2rem;
  font-size: 1rem;
  border-radius: 8px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: background-color 0.2s;
}

.start-btn {
  background-color: #4a9c6d;
  color: white;
}

.start-btn:hover {
  background-color: #3d8259;
}

.stop-btn {
  background-color: #c44b4b;
  color: white;
}

.stop-btn:hover {
  background-color: #a33d3d;
}

.connecting-btn {
  background-color: #888;
  color: white;
  cursor: not-allowed;
}
</style>