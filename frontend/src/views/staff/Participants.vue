<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import StatusBadge from '../../components/StatusBadge.vue'
const route=useRoute(), participants=ref([]),error=ref('')
onMounted(async()=>{try{participants.value=await api(`/staff/treks/${route.params.id}/participants`)}catch(e){error.value=e.message}})
</script>
<template>
  <PageHeader title="Participants" subtitle="Registered users for the assigned trek." />
  <div v-if="error" class="alert alert-danger">{{ error }}</div>
  <div class="card shadow-sm"><div class="table-responsive"><table class="table mb-0"><thead><tr><th>Name</th><th>Email</th><th>Status</th><th>Booked</th></tr></thead><tbody><tr v-for="p in participants" :key="p.id"><td>{{ p.user_name }}</td><td>{{ p.user_email }}</td><td><StatusBadge :status="p.status" /></td><td>{{ new Date(p.booking_date).toLocaleString() }}</td></tr></tbody></table></div></div>
</template>
