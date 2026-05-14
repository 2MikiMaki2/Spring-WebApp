<script setup>
import TextChat from '../components/TextChat.vue'
</script>

<template>
  <main>
    <TextChat />
  </main>
</template>

<style scoped>
main {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 2rem;
}

h1 {
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  main {
    padding: 0.5rem 1rem;
  }
}
</style>