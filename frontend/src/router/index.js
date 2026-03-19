import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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
  ],
})

// Navigation guard: before every page change, check if the user is logged in.
// If not, redirect to the login page. The login page itself is excluded
// from this check (otherwise you'd get an infinite redirect loop).
router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (!token && to.name !== 'login') {
    return { name: 'login' }
  }
})

export default router