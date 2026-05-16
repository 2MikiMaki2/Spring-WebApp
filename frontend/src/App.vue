<script setup>
import { ref, watch } from 'vue'
import { RouterLink, RouterView, useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const userName = ref(localStorage.getItem('userName') || '')
const isLoggedIn = ref(!!localStorage.getItem('token'))
const isGuest = ref(localStorage.getItem('isGuest') === 'true')

watch(
  () => route.path,
  () => {
    userName.value = localStorage.getItem('userName') || ''
    isLoggedIn.value = !!localStorage.getItem('token')
    isGuest.value = localStorage.getItem('isGuest') === 'true'
  },
)

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('userName')
  localStorage.removeItem('isGuest')
  isLoggedIn.value = false
  userName.value = ''
  router.push('/login')
}

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<template>
  <!-- Desktop top nav -->
  <header v-if="isLoggedIn" class="desktop-nav">
    <nav>
      <div class="nav-links">
        <RouterLink to="/" class="brand-link">frenchat</RouterLink>
        <RouterLink to="/voice">Voice</RouterLink>
        <RouterLink to="/text">Text</RouterLink>
        <RouterLink v-if="!isGuest" to="/history">History</RouterLink>
        <RouterLink to="/settings">Settings</RouterLink>
      </div>
      <div class="nav-user">
        <span class="user-name">{{ userName }}</span>
        <button @click="logout" class="logout-btn">Log out</button>
      </div>
    </nav>
  </header>

  <div :class="{ 'has-tab-bar': isLoggedIn }">
    <RouterView />
  </div>

  <!-- Mobile bottom tab bar -->
  <nav v-if="isLoggedIn" class="mobile-tab-bar">
    <RouterLink to="/" class="tab" :class="{ active: isActive('/') }">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
        <polyline points="9 22 9 12 15 12 15 22"/>
      </svg>
      <span>Home</span>
    </RouterLink>
    <RouterLink to="/voice" class="tab" :class="{ active: isActive('/voice') }">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
        <line x1="12" y1="19" x2="12" y2="23"/>
      </svg>
      <span>Voice</span>
    </RouterLink>
    <RouterLink to="/text" class="tab" :class="{ active: isActive('/text') }">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
      <span>Text</span>
    </RouterLink>
    <RouterLink v-if="!isGuest" to="/history" class="tab" :class="{ active: isActive('/history') }">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="9" y1="13" x2="15" y2="13"/>
        <line x1="9" y1="17" x2="13" y2="17"/>
      </svg>
      <span>History</span>
    </RouterLink>
    <RouterLink to="/settings" class="tab" :class="{ active: isActive('/settings') }">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="3"/>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
      </svg>
      <span>Settings</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
/* --- Desktop top nav --- */
.desktop-nav {
  padding: 1rem 2rem;
  border-bottom: 1px solid #ddd;
}

.desktop-nav nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1rem;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.nav-links a {
  text-decoration: none;
  color: #666;
}

.nav-links a.router-link-exact-active {
  color: #4a9c6d;
  font-weight: bold;
}

.nav-links a:hover {
  color: #4a9c6d;
}

.brand-link {
  font-weight: bold !important;
  color: #1D9E75 !important;
  font-size: 1.1rem;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-name {
  color: #888;
  font-size: 0.9rem;
}

.logout-btn {
  background: none;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 0.25rem 0.75rem;
  font-size: 0.85rem;
  color: #666;
  cursor: pointer;
}

.logout-btn:hover {
  border-color: #999;
  color: #333;
}

/* --- Mobile bottom tab bar --- */
.mobile-tab-bar {
  display: none;
}

/* --- Responsive --- */
@media (max-width: 768px) {
  .desktop-nav {
    display: none;
  }

  .has-tab-bar {
    padding-bottom: 70px;
  }

  .mobile-tab-bar {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #282828;
    padding: 6px 0 env(safe-area-inset-bottom, 4px);
    justify-content: space-around;
    align-items: center;
    z-index: 100;
  }

  .tab {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    text-decoration: none;
    color: #888;
    font-size: 10px;
    padding: 4px 8px;
  }

  .tab.active {
    color: #1D9E75;
  }
}
</style>