<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authHeaders, handleUnauthorized } from '../auth.js'
import { BACKEND_URL } from '../config.js'
import { friendlyError } from '../errors.js'

const router = useRouter()

const targetLanguage = ref('')
const voice = ref('')
const customPrompt = ref('')
const languages = ref([])
const voices = ref([])
const isLoading = ref(true)
const isSaving = ref(false)
const saveMessage = ref('')
const loadError = ref('')

onMounted(async () => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/preferences`, {
      headers: authHeaders(),
    })

    if (response.status === 401) {
      handleUnauthorized(router)
      return
    }

    const data = await response.json()
    targetLanguage.value = data.preferences.target_language
    voice.value = data.preferences.voice
    customPrompt.value = data.preferences.custom_prompt
    languages.value = data.options.languages
    voices.value = data.options.voices
  } catch (err) {
    console.error('Failed to load preferences:', err)
    loadError.value = friendlyError(err, 'Failed to load settings. Please refresh the page.')
  } finally {
    isLoading.value = false
  }
})

async function savePreferences() {
  isSaving.value = true
  saveMessage.value = ''

  try {
    const response = await fetch(`${BACKEND_URL}/api/preferences`, {
      method: 'PUT',
      headers: {
        ...authHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        target_language: targetLanguage.value,
        voice: voice.value,
        custom_prompt: customPrompt.value,
      }),
    })

    if (response.status === 401) {
      handleUnauthorized(router)
      return
    }

    if (!response.ok) {
      throw new Error('Failed to save')
    }

    saveMessage.value = 'Settings saved!'
    // Clear the success message after a few seconds.
    setTimeout(() => { saveMessage.value = '' }, 3000)
  } catch (err) {
    console.error('Save error:', err)
    saveMessage.value = 'Failed to save. Please try again.'
  } finally {
    isSaving.value = false
  }
}

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('userName')
  localStorage.removeItem('isGuest')
  router.push('/login')
}
</script>

<template>
  <main>
    <h1>Settings</h1>

    <div v-if="isLoading" class="loading">Loading preferences...</div>

    <div v-else-if="loadError" class="fc-error">{{ loadError }}</div>

    <div v-else class="settings-form">
      <div class="field">
        <label for="language">Language</label>
        <select id="language" v-model="targetLanguage">
          <option v-for="lang in languages" :key="lang" :value="lang">
            {{ lang }}
          </option>
        </select>
      </div>

      <div class="field">
        <label for="voice">AI Voice</label>
        <select id="voice" v-model="voice">
          <option v-for="v in voices" :key="v" :value="v">
            {{ v }}
          </option>
        </select>
      </div>

      <div class="field">
        <label for="custom-prompt">Custom Prompt (optional)</label>
        <textarea
          id="custom-prompt"
          v-model="customPrompt"
          rows="3"
          placeholder="e.g., I'm preparing for a job interview at a restaurant..."
        />
      </div>

      <button @click="savePreferences" :disabled="isSaving" class="save-btn">
        {{ isSaving ? 'Saving...' : 'Save' }}
      </button>

      <p v-if="saveMessage" class="save-message">{{ saveMessage }}</p>

      <button @click="logout" class="mobile-logout-btn">Log out</button>
    </div>
  </main>
</template>

<style scoped>
main {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: clamp(1.5rem, 4vw, 2.5rem) 0;
}

h1 {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(2rem, 4.5vw, 2.6rem);
  color: var(--text-strong);
  margin-bottom: 1.5rem;
}

.loading {
  color: var(--text-muted);
}

.settings-form {
  width: 100%;
  max-width: 460px;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  background: var(--surface-raised);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-rest);
  padding: clamp(1.5rem, 4vw, 2rem);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.field label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-body);
}

.field select,
.field textarea {
  padding: 0.6rem 0.7rem;
  font-size: 1rem;
  border: 1px solid var(--border-control);
  border-radius: var(--radius-control);
  font-family: inherit;
  background: var(--surface-page);
  color: var(--text-strong);
  transition: border-color 0.15s ease;
}

.field select:focus,
.field textarea:focus {
  outline: none;
  border-color: var(--brand);
}

.field textarea {
  resize: vertical;
}

.save-btn {
  padding: 0.65rem 1.6rem;
  font-size: 1rem;
  font-weight: 600;
  background-color: var(--brand);
  color: white;
  border: none;
  border-radius: var(--radius-control);
  cursor: pointer;
  align-self: flex-start;
  transition: background-color 0.15s ease;
}

.save-btn:hover:not(:disabled) {
  background-color: var(--brand-deep);
}

.save-btn:disabled {
  background-color: var(--border-control);
  cursor: not-allowed;
}

.save-message {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--accent-deep);
}

.mobile-logout-btn {
  display: none;
}

@media (max-width: 768px) {
  .mobile-logout-btn {
    display: block;
    margin-top: 1rem;
    padding: 0.65rem 1.6rem;
    font-size: 1rem;
    font-weight: 500;
    background: none;
    border: 1.5px solid var(--border-control);
    border-radius: var(--radius-control);
    color: var(--text-body);
    cursor: pointer;
    align-self: flex-start;
  }

  .mobile-logout-btn:hover {
    border-color: var(--brand);
    color: var(--brand-deep);
  }
}
</style>