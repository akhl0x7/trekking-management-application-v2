<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import StatusBadge from '../../components/StatusBadge.vue'
const bookings = ref([]); const error = ref('')
onMounted(async () => { try { bookings.value = await api('/admin/bookings') } catch (e) { error.value = e.message } })
</script>
<template>
  <PageHeader title="All bookings" subtitle="Review current and historical trek bookings." />
  <div v-if="error" class="alert alert-danger">{{ error }}</div>
  <div class="card shadow-sm"><div class="table-responsive"><table class="table align-middle mb-0"><thead><tr><th>Trekker</th><th>Trek</th><th>Dates</th><th>Status</th><th>Booked at</th></tr></thead><tbody><tr v-for="b in bookings" :key="b.id"><td>{{ b.user_name }}</td><td>{{ b.trek_name }}<div class="small text-secondary">{{ b.location }}</div></td><td>{{ b.start_date }} → {{ b.end_date }}</td><td><StatusBadge :status="b.status" /></td><td>{{ new Date(b.booking_date).toLocaleString() }}</td></tr></tbody></table></div></div>
</template>
