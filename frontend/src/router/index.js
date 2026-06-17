import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/welcome',
      name: 'welcome',
      component: () => import('../views/WelcomeView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/voice',
      name: 'voice',
      component: () => import('../views/VoiceChatView.vue'),
    },
    {
      path: '/text',
      name: 'text',
      component: () => import('../views/TextChatView.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('../views/HistoryView.vue'),
    },
    {
      path: '/history/:id',
      name: 'conversation',
      component: () => import('../views/ConversationView.vue'),
    },
  ],
})

// Pages reachable without being signed in.
const PUBLIC_PAGES = ['welcome', 'login']

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (!token && !PUBLIC_PAGES.includes(to.name)) {
    // Logged-out visitors land on the welcome page.
    return { name: 'welcome' }
  }

  // Signed-in users have no reason to see the marketing/login pages.
  if (token && PUBLIC_PAGES.includes(to.name)) {
    return { name: 'home' }
  }

  const isGuest = localStorage.getItem('isGuest') === 'true'
  if (isGuest && (to.name === 'history' || to.name === 'conversation')) {
    return { name: 'home' }
  }
})

export default router