import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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

export default router