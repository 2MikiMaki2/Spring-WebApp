import { BACKEND_URL } from './config.js'

export function authHeaders() {
  return { Authorization: `Bearer ${localStorage.getItem('token')}` }
}

export function handleUnauthorized(router) {
  localStorage.removeItem('token')
  localStorage.removeItem('userName')
  localStorage.removeItem('isGuest')
  router.push('/login')
}

export async function saveConversation(messages, mode) {
  if (messages.length === 0) return

  await fetch(`${BACKEND_URL}/api/conversations`, {
    method: 'POST',
    headers: {
      ...authHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ mode, messages }),
  })
}