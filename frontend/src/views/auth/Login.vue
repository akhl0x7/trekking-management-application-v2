<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '../../stores/auth'
import AlertMessage from '../../components/AlertMessage.vue'

const router = useRouter()
const email = ref('admin@tma.local')
const password = ref('Admin@12345')
const error = ref('')
const loading = ref(false)

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(email.value, password.value)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="row justify-content-center py-5">
    <div class="col-md-5 col-lg-4">
      <div class="card shadow-sm p-4">
        <h1 class="h3 mb-1">Sign in</h1>
        <p class="text-secondary mb-4">Trekking Management Application</p>
        <AlertMessage :message="error" />
        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="email" type="email" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="password" type="password" class="form-control" required />
          </div>
          <button class="btn btn-dark w-100" :disabled="loading">{{ loading ? 'Signing in…' : 'Sign in' }}</button>
        </form>
        <router-link class="btn btn-link mt-3" to="/register">Create trekker account</router-link>
      </div>
    </div>
  </div>
</template>
