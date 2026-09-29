<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from './stores/auth'

const router = useRouter()

const links = computed(() => {
  if (auth.user?.role === 'ADMIN') return [
    ['/dashboard', 'Dashboard'],
    ['/admin/treks', 'Treks'],
    ['/admin/staff', 'Staff'],
    ['/admin/users', 'Users'],
    ['/admin/bookings', 'Bookings'],
    ['/admin/reports', 'Reports']
  ]
  if (auth.user?.role === 'STAFF') return [
    ['/dashboard', 'Dashboard'],
    ['/staff/treks', 'Assigned Treks']
  ]
  if (auth.user?.role === 'TREKKER') return [
    ['/dashboard', 'Dashboard'],
    ['/trekker/treks', 'Browse Treks'],
    ['/trekker/bookings', 'Bookings'],
    ['/trekker/history', 'History'],
    ['/trekker/profile', 'Profile']
  ]
  return []
})

async function logout() {
  await auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-vh-100 bg-body-tertiary">
    <nav v-if="auth.user" class="navbar navbar-expand-lg bg-dark navbar-dark sticky-top">
      <div class="container-fluid px-4">
        <router-link class="navbar-brand fw-bold" to="/dashboard">TMA</router-link>
        <div class="d-flex flex-wrap gap-1 align-items-center">
          <router-link v-for="[href, label] in links" :key="href" :to="href" class="nav-link text-white-50 px-2" :class="{ active: $route.path === href }">{{ label }}</router-link>
        </div>
        <div class="ms-auto d-flex align-items-center gap-3">
          <span class="small text-white-50">{{ auth.user.name }}</span>
          <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
        </div>
      </div>
    </nav>
    <main class="container-fluid px-4 py-4">
      <router-view />
    </main>
  </div>
</template>
