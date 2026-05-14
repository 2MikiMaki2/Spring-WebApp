/**
 * Returns a user-friendly error message based on the error type.
 * - Network errors (TypeError from fetch) → connection message
 * - Everything else → generic fallback
 */
export function friendlyError(err, fallback = 'Something went wrong. Please try again.') {
  if (err instanceof TypeError && err.message === 'Failed to fetch') {
    return 'Unable to connect. Please check your internet connection.'
  }
  return fallback
}