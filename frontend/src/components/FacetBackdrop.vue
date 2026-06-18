<script setup>
// Shared signature backdrop (DESIGN §6b): a fixed, near-white low-poly faceted
// dome with a faint teal wash beneath. Sits behind the page foreground
// (z-index 0); foreground sections lift above it with position:relative;z-index:1.
// Used on the home and welcome pages.
</script>

<template>
  <div class="facet-backdrop" aria-hidden="true">
    <span class="facet-teal-wash"></span>
    <img class="facet-img" src="/frenchat-facets.svg" alt="" />
  </div>
</template>

<style scoped>
.facet-backdrop {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.facet-teal-wash {
  position: absolute;
  bottom: -150px;
  right: -80px;
  width: 460px;
  height: 420px;
  border-radius: 50%;
  background: var(--facet-teal-wash);
  filter: blur(18px);
}

.facet-img {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: var(--facet-width);
  max-width: none;
  height: auto;
}
</style>
