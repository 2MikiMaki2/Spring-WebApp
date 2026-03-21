<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { BACKEND_URL } from '../config.js'
const router = useRouter()
const isLoading = ref(true)
const errorMessage = ref('')

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
</script>

<template>
  <main>
    <h1>Language Practice</h1>
    <p class="subtitle">Sign in to get started</p>

    <div v-show="isLoading" class="loading">Loading...</div>
    <div v-show="!isLoading" id="google-signin-btn"></div>
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
</style>