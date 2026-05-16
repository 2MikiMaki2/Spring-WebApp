<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { BACKEND_URL } from '../config.js'
import { friendlyError } from '../errors.js'

const router = useRouter()
const isLoading = ref(true)
const errorMessage = ref('')
const isGuestLoading = ref(false)

// The Google script loads asynchronously, so it might not be ready
// when this component mounts. This function polls until it's available.
function waitForGoogle() {
  return new Promise((resolve) => {
    if (window.google?.accounts?.id) {
      resolve()
      return
    }
    const interval = setInterval(() => {
      if (window.google?.accounts?.id) {
        clearInterval(interval)
        resolve()
      }
    }, 100)
  })
}

onMounted(async () => {
  try {
    // Fetch our Google Client ID from the backend and wait for
    // the Google script to load — both happen in parallel.
    const [configResponse] = await Promise.all([
      fetch(`${BACKEND_URL}/api/auth/config`),
      waitForGoogle(),
    ])
    const config = await configResponse.json()

    // Initialize Google's sign-in library with our client ID.
    // The callback fires after the user picks their Google account.
    window.google.accounts.id.initialize({
      client_id: config.google_client_id,
      callback: handleGoogleResponse,
    })

    // Render the official Google sign-in button into our placeholder div.
    window.google.accounts.id.renderButton(
      document.getElementById('google-signin-btn'),
      { theme: 'outline', size: 'large', text: 'signin_with' },
    )

    isLoading.value = false
  } catch (err) {
    console.error('Login setup error:', err)
    errorMessage.value = 'Failed to load sign-in. Please refresh.'
    isLoading.value = false
  }
})

async function handleGoogleResponse(response) {
  // Google gives us a "credential" — an ID token proving who the user is.
  // We send it to our backend, which verifies it and returns our own JWT.
  try {
    const result = await fetch(`${BACKEND_URL}/api/auth/google`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ credential: response.credential }),
    })

    if (!result.ok) {
      throw new Error('Authentication failed')
    }

    const data = await result.json()
    localStorage.setItem('token', data.token)
    localStorage.setItem('userName', data.user.name)
    router.push('/')
  } catch (err) {
    console.error('Auth error:', err)
    errorMessage.value = 'Sign-in failed. Please try again.'
  }
}

async function loginAsGuest() {
  isGuestLoading.value = true
  errorMessage.value = ''

  try {
    const result = await fetch(`${BACKEND_URL}/api/auth/guest`, {
      method: 'POST',
    })

    if (!result.ok) {
      throw new Error('Failed to create guest session')
    }

    const data = await result.json()
    localStorage.setItem('token', data.token)
    localStorage.setItem('userName', data.user.name)
    localStorage.setItem('isGuest', 'true')
    router.push('/')
  } catch (err) {
    console.error('Guest auth error:', err)
    errorMessage.value = friendlyError(err, 'Could not start guest session. Please try again.')
    isGuestLoading.value = false
  }
}
</script>

<template>
  <main>
    <h1>Language Practice</h1>
    <p class="subtitle">Sign in to get started</p>

    <div v-show="isLoading" class="loading">Loading...</div>
    <div v-show="!isLoading" id="google-signin-btn"></div>

    <div v-show="!isLoading" class="divider">
      <span>or</span>
    </div>

    <button
      v-show="!isLoading"
      @click="loginAsGuest"
      :disabled="isGuestLoading"
      class="guest-btn"
    >
      {{ isGuestLoading ? 'Starting...' : 'Try as Guest' }}
    </button>

    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </main>
</template>

<style scoped>
main {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4rem 2rem;
}

h1 {
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #888;
  margin-bottom: 2rem;
}

.loading {
  color: #888;
}

.error {
  color: #c44b4b;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  main {
    padding: 2rem 1rem;
  }
}

.divider {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 230px;
  margin: 1rem 0;
  color: #aaa;
  font-size: 0.85rem;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #ddd;
}

.divider span {
  padding: 0 0.75rem;
}

.guest-btn {
  padding: 0.6rem 1.5rem;
  font-size: 0.95rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: none;
  color: #666;
  cursor: pointer;
}

.guest-btn:hover:not(:disabled) {
  border-color: #999;
  color: #333;
}

.guest-btn:disabled {
  color: #aaa;
  cursor: not-allowed;
}
</style>