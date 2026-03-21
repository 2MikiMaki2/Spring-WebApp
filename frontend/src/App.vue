<script setup>
import { ref, watch } from 'vue'
import { RouterLink, RouterView, useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const userName = ref(localStorage.getItem('userName') || '')
const isLoggedIn = ref(!!localStorage.getItem('token'))

watch(
  () => route.path,
  () => {
    userName.value = localStorage.getItem('userName') || ''
    isLoggedIn.value = !!localStorage.getItem('token')
  },
)

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('userName')
  isLoggedIn.value = false
  userName.value = ''
  router.push('/login')
}
</script>

<template>
  <header v-if="isLoggedIn">
    <nav>
      <div class="nav-links">
        <RouterLink to="/" class="brand-link">frenchat</RouterLink>
        <RouterLink to="/voice">Voice</RouterLink>
        <RouterLink to="/text">Text</RouterLink>
        <RouterLink to="/history">History</RouterLink>
        <RouterLink to="/settings">Settings</RouterLink>
      </div>
      <div class="nav-user">
        <span class="user-name">{{ userName }}</span>
        <button @click="logout" class="logout-btn">Log out</button>
      </div>
    </nav>
  </header>

  <RouterView />
</template>

<style scoped>
header {
  padding: 1rem 2rem;
  border-bottom: 1px solid #ddd;
}

nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1rem;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
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

.brand-link {
  font-weight: bold;
  color: #1D9E75 !important;
  font-size: 1.1rem;
}
</style>