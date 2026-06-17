<script setup>
import { RouterLink } from 'vue-router'
import BrandLogo from '../components/BrandLogo.vue'

const mission =
  'We believe fluency comes from conversation, not flashcards. frenchat exists ' +
  'to give everyone a patient, judgment-free partner to talk with — so that ' +
  'learning French feels less like studying and more like making a friend.'
</script>

<template>
  <div class="welcome">
    <!-- NAV -->
    <header class="nav">
      <RouterLink to="/welcome" class="nav-brand"><BrandLogo size="md" /></RouterLink>
      <nav class="nav-links">
        <a href="#mission" class="nav-mission">Mission</a>
        <RouterLink to="/login" class="nav-login">Log in</RouterLink>
      </nav>
    </header>

    <!-- HERO -->
    <section class="hero">
      <div class="blob blob-coral"></div>
      <div class="blob blob-teal"></div>

      <h1 class="hero-title">
        Learn French by <span class="hl">talking</span>, not cramming
      </h1>
      <p class="hero-sub">
        Practice real conversations with an AI partner that listens, replies, and
        gently nudges you forward — by voice or by text, whenever you have a few
        minutes.
      </p>
      <div class="hero-cta">
        <RouterLink to="/login" class="cta-primary">Start practicing — it's free</RouterLink>
      </div>
    </section>

    <!-- MISSION -->
    <section id="mission" class="mission">
      <div class="mission-card">
        <div class="mission-bar"></div>
        <span class="fc-section-label mission-label">Our mission</span>
        <p class="mission-text">{{ mission }}</p>
      </div>
    </section>

    <!-- FOOTER -->
    <footer class="footer">
      <BrandLogo size="sm" />
      <nav class="footer-links">
        <a href="#" target="_blank" rel="noopener" class="footer-link footer-link-linkedin">
          <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor"><path d="M4.98 3.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-.95 1.83-1.95 3.76-1.95 4.02 0 4.76 2.5 4.76 5.76V21h-4v-5.1c0-1.22-.02-2.78-1.7-2.78-1.7 0-1.96 1.32-1.96 2.69V21H9z"/></svg>
          LinkedIn
        </a>
        <a href="#" target="_blank" rel="noopener" class="footer-link footer-link-photo">
          <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.6"/><path d="M21 15l-5-5L5 21"/></svg>
          Photography
        </a>
      </nav>
    </footer>
  </div>
</template>

<style scoped>
/* Full-bleed: break out of the centered #app column so the landing spans the
   whole viewport. */
.welcome {
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
  width: 100vw;
  min-height: 100vh;
  background: radial-gradient(130% 80% at 50% -8%, #FFF4E8 0%, #FBF6EF 44%, #F6EFE4 100%);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* --- NAV --- */
.nav {
  position: relative;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 14px 28px;
  padding: 22px clamp(20px, 5vw, 64px);
}

.nav-brand {
  display: inline-flex;
  align-items: center;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: clamp(14px, 2vw, 32px);
  flex-wrap: wrap;
}

.nav-mission {
  font-weight: 500;
  font-size: 15px;
  color: var(--text-muted);
  transition: color 0.15s ease;
}

.nav-mission:hover {
  color: var(--text-strong);
}

.nav-login {
  font-weight: 600;
  font-size: 14px;
  color: #fff;
  background: var(--brand);
  border-radius: var(--radius-control);
  padding: 10px 20px;
  box-shadow: 0 8px 20px rgba(238, 138, 95, 0.28);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.nav-login:hover {
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 12px 26px rgba(238, 138, 95, 0.36);
}

/* --- HERO --- */
.hero {
  position: relative;
  padding: clamp(40px, 7vw, 92px) clamp(20px, 5vw, 64px) clamp(36px, 5vw, 64px);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.blob {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  animation: fc-float 7s ease-in-out infinite;
}

.blob-coral {
  top: -30px;
  left: 6%;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle at 30% 30%, var(--brand-tint), transparent 70%);
}

.blob-teal {
  bottom: -50px;
  right: 8%;
  width: 240px;
  height: 240px;
  background: radial-gradient(circle at 40% 40%, var(--accent-tint), transparent 70%);
  animation-duration: 9s;
}

@keyframes fc-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.hero-title {
  position: relative;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(2.8rem, 7vw, 5rem);
  line-height: 1.02;
  letter-spacing: 0.005em;
  color: var(--text-strong);
  margin: 0 0 20px;
  max-width: 14ch;
}

.hero-title .hl {
  font-style: italic;
  color: var(--brand);
}

.hero-sub {
  position: relative;
  font-size: clamp(1.05rem, 2vw, 1.3rem);
  line-height: 1.55;
  color: var(--text-muted);
  margin: 0 0 34px;
  max-width: 54ch;
}

.hero-cta {
  position: relative;
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  justify-content: center;
}

.cta-primary {
  font-weight: 600;
  font-size: 1.02rem;
  color: #fff;
  background: var(--brand);
  border-radius: 14px;
  padding: 15px 30px;
  box-shadow: 0 12px 28px rgba(238, 138, 95, 0.32);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.cta-primary:hover {
  color: #fff;
  transform: translateY(-3px);
  box-shadow: 0 18px 38px rgba(238, 138, 95, 0.42);
}

/* --- MISSION --- */
.mission {
  padding: clamp(20px, 4vw, 40px) clamp(20px, 5vw, 64px) clamp(48px, 6vw, 80px);
  display: flex;
  justify-content: center;
}

.mission-card {
  position: relative;
  width: 100%;
  max-width: 880px;
  background: var(--surface-raised);
  border: 1px solid var(--border);
  border-radius: 30px;
  box-shadow: 0 18px 50px rgba(120, 90, 55, 0.08);
  padding: clamp(34px, 5vw, 60px);
  text-align: center;
  overflow: hidden;
}

.mission-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background: linear-gradient(90deg, var(--brand), var(--accent));
}

.mission-label {
  display: inline-block;
  letter-spacing: 0.1em;
  margin-bottom: 20px;
}

.mission-text {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(1.5rem, 3.2vw, 2.2rem);
  line-height: 1.32;
  color: var(--text-strong);
  margin: 0;
}

/* --- FOOTER --- */
.footer {
  margin-top: auto;
  border-top: 1px solid #EFE5D7;
  padding: 30px clamp(20px, 5vw, 64px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 18px;
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.footer-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  color: #7A6F60;
  background: var(--surface-raised);
  border: 1px solid #EFE5D7;
  border-radius: var(--radius-control);
  padding: 10px 16px;
  transition: border-color 0.18s ease, color 0.18s ease, transform 0.18s ease;
}

.footer-link-linkedin:hover {
  border-color: var(--brand);
  color: var(--brand);
  transform: translateY(-2px);
}

.footer-link-photo:hover {
  border-color: var(--accent);
  color: var(--accent);
  transform: translateY(-2px);
}
</style>
