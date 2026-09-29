import { reactive } from 'vue'
import { api } from '../api'

export const auth = reactive({
  user: null,
  loading: false,
  loaded: false,
  async load() {
    if (this.loaded) return
    this.loading = true
    try {
      this.user = await api('/auth/me')
    } catch {
      this.user = null
    } finally {
      this.loading = false
      this.loaded = true
    }
  },
  async login(email, password) {
    this.user = await api('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    })
    this.loaded = true
  },
  async register(payload) {
    this.user = await api('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
    this.loaded = true
  },
  async logout() {
    await api('/auth/logout', { method: 'POST' })
    this.user = null
    this.loaded = true
  }
})
