<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <nav>
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/voice">Voice</RouterLink>
      <RouterLink to="/text">Text</RouterLink>
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
  gap: 1.5rem;
  font-size: 1rem;
}

nav a {
  text-decoration: none;
  color: #666;
}

nav a.router-link-exact-active {
  color: #4a9c6d;
  font-weight: bold;
}

nav a:hover {
  color: #4a9c6d;
}
</style>