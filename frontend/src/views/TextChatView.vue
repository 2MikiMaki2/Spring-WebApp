<script setup>
import TextChat from '../components/TextChat.vue'
</script>

<template>
  <main>
    <h1>Text Practice</h1>
    <TextChat />
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
  margin-bottom: 1rem;
}
</style>