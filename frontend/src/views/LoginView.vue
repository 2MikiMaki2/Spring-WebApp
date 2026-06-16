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
    <h1>frenchat</h1>
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

    <p v-if="errorMessage" class="fc-error login-error">{{ errorMessage }}</p>
  </main>
</template>

<style scoped>
main {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
  padding: clamp(2rem, 6vw, 4rem) 0;
}

h1 {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(2.6rem, 7vw, 3.8rem);
  color: var(--brand);
  margin-bottom: 0.4rem;
}

.subtitle {
  color: var(--text-muted);
  margin-bottom: 2rem;
}

.loading {
  color: var(--text-muted);
}

.login-error {
  margin-top: 1rem;
}

.divider {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 230px;
  margin: 1.25rem 0;
  color: var(--text-faint);
  font-size: 0.85rem;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid var(--border);
}

.divider span {
  padding: 0 0.75rem;
}

.guest-btn {
  padding: 0.65rem 1.6rem;
  font-size: 0.95rem;
  font-weight: 500;
  border: 1.5px solid var(--border-control);
  border-radius: var(--radius-control);
  background: none;
  color: var(--text-body);
  cursor: pointer;
  transition: border-color 0.15s ease, background-color 0.15s ease, color 0.15s ease;
}

.guest-btn:hover:not(:disabled) {
  border-color: var(--brand);
  background-color: var(--brand-tint);
  color: var(--brand-deep);
}

.guest-btn:disabled {
  color: var(--text-faint);
  cursor: not-allowed;
}
</style>