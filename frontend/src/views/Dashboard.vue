<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api'
import { auth } from '../stores/auth'
import PageHeader from '../components/PageHeader.vue'
import StatusBadge from '../components/StatusBadge.vue'
import AlertMessage from '../components/AlertMessage.vue'

const data = ref(null)
const error = ref('')

async function load() {
  error.value = ''
  try {
    if (auth.user.role === 'ADMIN') data.value = await api('/admin/dashboard')
    else if (auth.user.role === 'STAFF') data.value = await api('/staff/dashboard')
    else data.value = await api('/trekker/dashboard')
  } catch (e) {
    error.value = e.message
  }
}

onMounted(load)
</script>

<template>
  <PageHeader title="Dashboard" subtitle="Overview of current trekking activity."><button class="btn btn-outline-dark" @click="load">Refresh</button></PageHeader>
  <AlertMessage :message="error" />
  <div v-if="auth.user.role === 'ADMIN' && data" class="row g-3">
    <div v-for="item in [['Treks', data.treks], ['Open treks', data.open_treks], ['Users', data.users], ['Staff', data.staff], ['Bookings', data.bookings]]" :key="item[0]" class="col-sm-6 col-xl-3"><div class="card shadow-sm p-4"><div class="text-secondary">{{ item[0] }}</div><div class="metric">{{ item[1] }}</div></div></div>
  </div>
  <div v-else-if="auth.user.role === 'STAFF' && data" class="row g-3">
    <div class="col-sm-6"><div class="card shadow-sm p-4"><div class="text-secondary">Assigned treks</div><div class="metric">{{ data.assigned_treks }}</div></div></div>
    <div class="col-sm-6"><div class="card shadow-sm p-4"><div class="text-secondary">Registered users</div><div class="metric">{{ data.registered_users }}</div></div></div>
    <div class="col-12"><div class="card shadow-sm p-4"><h2 class="h5">Assigned treks</h2><div v-for="trek in data.treks" :key="trek.id" class="border rounded p-3 mb-2"><div class="d-flex justify-content-between"><strong>{{ trek.name }}</strong><StatusBadge :status="trek.status" /></div><div class="text-secondary small">{{ trek.location }} · {{ trek.start_date }} · {{ trek.available_slots }} slots</div></div></div></div>
  </div>
  <div v-else-if="auth.user.role === 'TREKKER' && data" class="row g-3">
    <div class="col-sm-6"><div class="card shadow-sm p-4"><div class="text-secondary">Current bookings</div><div class="metric">{{ data.booked_treks.length }}</div></div></div>
    <div class="col-sm-6"><div class="card shadow-sm p-4"><div class="text-secondary">History records</div><div class="metric">{{ data.history_count }}</div></div></div>
    <div class="col-12"><div class="hero rounded-4 p-5"><h2 class="display-6 fw-semibold">Explore the next trail.</h2><p class="lead mb-0">Browse open treks, check availability and reserve your place.</p></div></div>
  </div>
</template>
