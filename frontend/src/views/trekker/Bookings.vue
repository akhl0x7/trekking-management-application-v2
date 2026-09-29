<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import StatusBadge from '../../components/StatusBadge.vue'
const bookings=ref([]),error=ref(''),message=ref('')
async function load(){try{bookings.value=await api('/trekker/bookings')}catch(e){error.value=e.message}}
async function cancel(id){if(!confirm('Cancel this booking?'))return;try{await api(`/trekker/bookings/${id}/cancel`,{method:'POST'});message.value='Booking cancelled.';await load()}catch(e){error.value=e.message}}
onMounted(load)
</script>
<template><PageHeader title="My bookings" subtitle="Current reservations and their status."/><div v-if="error" class="alert alert-danger">{{ error }}</div><div v-if="message" class="alert alert-success">{{ message }}</div><div class="card shadow-sm"><div class="table-responsive"><table class="table align-middle mb-0"><thead><tr><th>Trek</th><th>Dates</th><th>Status</th><th></th></tr></thead><tbody><tr v-for="b in bookings" :key="b.id"><td><strong>{{ b.trek_name }}</strong><div class="small text-secondary">{{ b.location }}</div></td><td>{{ b.start_date }} → {{ b.end_date }}</td><td><StatusBadge :status="b.status" /></td><td class="text-end"><button v-if="b.status==='BOOKED'" class="btn btn-sm btn-outline-danger" @click="cancel(b.id)">Cancel</button></td></tr></tbody></table></div></div></template>
