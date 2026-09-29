<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '../../stores/auth'
import AlertMessage from '../../components/AlertMessage.vue'

const router = useRouter()
const form = ref({ name: '', email: '', password: '' })
const error = ref('')
const loading = ref(false)

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await auth.register(form.value)
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
    <div class="col-md-6 col-lg-5">
      <div class="card shadow-sm p-4">
        <h1 class="h3">Create trekker account</h1>
        <p class="text-secondary">Registration is available for trekkers.</p>
        <AlertMessage :message="error" />
        <form @submit.prevent="submit">
          <div class="mb-3"><label class="form-label">Name</label><input v-model="form.name" class="form-control" required /></div>
          <div class="mb-3"><label class="form-label">Email</label><input v-model="form.email" type="email" class="form-control" required /></div>
          <div class="mb-3"><label class="form-label">Password</label><input v-model="form.password" type="password" class="form-control" minlength="8" required /></div>
          <button class="btn btn-dark w-100" :disabled="loading">{{ loading ? 'Creating…' : 'Create account' }}</button>
        </form>
        <router-link class="btn btn-link mt-3" to="/login">Back to sign in</router-link>
      </div>
    </div>
  </div>
</template>
