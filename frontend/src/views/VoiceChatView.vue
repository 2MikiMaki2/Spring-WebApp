<script setup>
import VoiceChat from '../components/VoiceChat.vue'
</script>

<template>
  <main>
    <h1>Voice Practice</h1>
    <VoiceChat />
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