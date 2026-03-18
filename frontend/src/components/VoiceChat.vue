<script setup>
import { ref, onUnmounted } from 'vue'

const BACKEND_URL = 'https://backend-production-2cd9.up.railway.app'

// Reactive state that the template reads to update the UI.
const status = ref('idle') // idle | connecting | connected | error
const errorMessage = ref('')

// These are not reactive — the template doesn't need to read them.
// They're just references we hold so we can clean them up later.
let peerConnection = null
let dataChannel = null
let audioElement = null
let mediaStream = null

async function startConversation() {
  status.value = 'connecting'
  errorMessage.value = ''

  try {
    // Step 1: Get an ephemeral token from our backend.
    const tokenResponse = await fetch(`${BACKEND_URL}/api/token`, {
      method: 'POST',
    })
    if (!tokenResponse.ok) {
      throw new Error('Failed to get token from backend')
    }
    const tokenData = await tokenResponse.json()
    const ephemeralKey = tokenData.value

    // Step 2: Create a WebRTC peer connection.
    // This is the object that manages the audio connection to OpenAI.
    const pc = new RTCPeerConnection()
    peerConnection = pc

    // Step 3: Set up audio playback.
    // When OpenAI sends audio back, it arrives as a "track" on the
    // peer connection. We pipe it into an <audio> element to play it.
    audioElement = document.createElement('audio')
    audioElement.autoplay = true
    pc.ontrack = (event) => {
      audioElement.srcObject = event.streams[0]
    }

    // Step 4: Capture the user's microphone and add it to the connection.
    // getUserMedia asks the browser for mic access — the user will see
    // a permission popup the first time.
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
    pc.addTrack(mediaStream.getTracks()[0])

    // Step 5: Create a "data channel" for sending/receiving control events.
    // OpenAI uses this channel for things like session updates and
    // conversation events. We listen for open/close to track status.
    dataChannel = pc.createDataChannel('oai-events')
    dataChannel.onopen = () => {
      status.value = 'connected'
    }

    // Step 6: SDP handshake — this is how WebRTC connections are established.
    // Our browser creates an "offer" describing what it can do (send audio,
    // receive audio, etc.), and OpenAI responds with an "answer" accepting.
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

    // If the connection drops unexpectedly, update the status.
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

function stopConversation() {
  // Close the data channel.
  if (dataChannel) {
    dataChannel.close()
    dataChannel = null
  }

  // Close the peer connection (stops all audio streaming).
  if (peerConnection) {
    peerConnection.close()
    peerConnection = null
  }

  // Release the microphone so the browser tab doesn't keep showing
  // the "recording" indicator.
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop())
    mediaStream = null
  }

  // Clean up the audio playback element.
  if (audioElement) {
    audioElement.srcObject = null
    audioElement = null
  }

  // Only reset to idle if we're not showing an error.
  if (status.value !== 'error') {
    status.value = 'idle'
  }
}

// If the user navigates away from this page, clean up the connection.
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