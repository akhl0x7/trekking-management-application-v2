export async function api(path, options = {}) {
  const response = await fetch(`/api/v1${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  })
  const body = await response.json().catch(() => ({ data: null, error: { message: 'Invalid server response' } }))
  if (!response.ok) throw new Error(body.error?.message || 'Request failed')
  return body.data
}
