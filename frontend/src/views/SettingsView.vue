<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const BACKEND_URL = 'https://backend-production-2cd9.up.railway.app'
const router = useRouter()

const targetLanguage = ref('')
const voice = ref('')
const customPrompt = ref('')
const languages = ref([])
const voices = ref([])
const isLoading = ref(true)
const isSaving = ref(false)
const saveMessage = ref('')

function authHeaders() {
  return { Authorization: `Bearer ${localStorage.getItem('token')}` }
}

onMounted(async () => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/preferences`, {
      headers: authHeaders(),
    })

    if (response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userName')
      router.push('/login')
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
      localStorage.removeItem('token')
      localStorage.removeItem('userName')
      router.push('/login')
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
</script>

<template>
  <main>
    <h1>Settings</h1>

    <div v-if="isLoading" class="loading">Loading preferences...</div>

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
    </div>
  </main>
</template>

<style scoped>
main {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
}

h1 {
  margin-bottom: 1.5rem;
}

.loading {
  color: #888;
}

.settings-form {
  width: 100%;
  max-width: 450px;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.field label {
  font-size: 0.9rem;
  font-weight: bold;
  color: #888;
}

.field select,
.field textarea {
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-family: inherit;
  background: #fff;
  color: #333;
}

.field textarea {
  resize: vertical;
}

.save-btn {
  padding: 0.6rem 1.5rem;
  font-size: 1rem;
  background-color: #4a9c6d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  align-self: flex-start;
}

.save-btn:hover:not(:disabled) {
  background-color: #3d8259;
}

.save-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.save-message {
  font-size: 0.9rem;
  color: #4a9c6d;
}
</style>