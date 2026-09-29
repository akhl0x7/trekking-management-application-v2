<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
const report = ref(null); const error = ref('')
onMounted(async () => { try { report.value = await api('/admin/reports') } catch (e) { error.value = e.message } })
</script>
<template>
  <PageHeader title="Reports" subtitle="Current trekking activity statistics." />
  <div v-if="error" class="alert alert-danger">{{ error }}</div>
  <div v-if="report" class="row g-3"><div class="col-md-4"><div class="card shadow-sm p-4"><div class="text-secondary">Treks conducted</div><div class="metric">{{ report.treks_conducted }}</div></div></div><div class="col-md-4"><div class="card shadow-sm p-4"><div class="text-secondary">Users participated</div><div class="metric">{{ report.users_participated }}</div></div></div><div class="col-12"><div class="card shadow-sm p-4"><h2 class="h5">Popular treks</h2><div v-for="item in report.popular_treks" :key="item.name" class="d-flex justify-content-between border-bottom py-2"><span>{{ item.name }}</span><strong>{{ item.bookings }}</strong></div><div v-if="!report.popular_treks.length" class="text-secondary">No completed activity yet.</div></div></div></div>
</template>
