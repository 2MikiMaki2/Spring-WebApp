<script setup>
// The frenchat brand mark: a "typing…" chat-bubble logomark + Baloo 2 wordmark.
// Reused in the app nav, the welcome header, and footers. See DESIGN.md §4b.
defineProps({
  // 'md' for nav / welcome header, 'sm' for footers.
  size: {
    type: String,
    default: 'md',
  },
})
</script>

<template>
  <span class="brand-logo" :class="`brand-logo-${size}`">
    <span class="bubble">
      <span class="dot dot-1"></span>
      <span class="dot dot-2"></span>
      <span class="dot dot-3"></span>
    </span>
    <span class="wordmark">frenchat</span>
  </span>
</template>

<style scoped>
.brand-logo {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  line-height: 1;
}

.bubble {
  background: var(--surface-raised);
  border: 2px solid var(--logo-bubble-border);
  border-radius: 12px 12px 12px 4px; /* small bottom-left corner = chat tail */
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 16px rgba(120, 90, 55, 0.08);
}

.dot {
  border-radius: 50%;
}

.dot-1 { background: var(--brand); }
.dot-2 { background: var(--brand-light); }
.dot-3 { background: var(--logo-dot-dark); }

.wordmark {
  font-family: var(--font-logo);
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--brand);
}

/* --- size: md (nav / welcome header) --- */
.brand-logo-md .bubble {
  width: 42px;
  height: 35px;
  gap: 5px;
}

.brand-logo-md .dot {
  width: 8px;
  height: 8px;
}

.brand-logo-md .wordmark {
  font-size: 22px;
}

/* --- size: sm (footers) --- */
.brand-logo-sm {
  gap: 9px;
}

.brand-logo-sm .bubble {
  width: 34px;
  height: 29px;
  gap: 4px;
  border-radius: 10px 10px 10px 3px;
}

.brand-logo-sm .dot {
  width: 6px;
  height: 6px;
}

.brand-logo-sm .wordmark {
  font-size: 17px;
}
</style>
