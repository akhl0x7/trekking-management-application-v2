<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import StatusBadge from '../../components/StatusBadge.vue'
const treks=ref([]),error=ref(''),message=ref('')
async function load(){try{treks.value=await api('/staff/treks');error.value=''}catch(e){error.value=e.message}}
async function update(id,payload){try{await api(`/staff/treks/${id}`,{method:'PATCH',body:JSON.stringify(payload)});message.value='Trek updated.';await load()}catch(e){error.value=e.message}}
async function start(id){try{await api(`/staff/treks/${id}/start`,{method:'POST'});message.value='Trek marked as started.';await load()}catch(e){error.value=e.message}}
async function complete(id){try{await api(`/staff/treks/${id}/complete`,{method:'POST'});message.value='Trek completed.';await load()}catch(e){error.value=e.message}}
onMounted(load)
</script>
<template>
  <PageHeader title="Assigned treks" subtitle="Manage assigned trekking events and participants." />
  <div v-if="error" class="alert alert-danger">{{ error }}</div><div v-if="message" class="alert alert-success">{{ message }}</div>
  <div class="row g-3"><div v-for="trek in treks" :key="trek.id" class="col-lg-6"><div class="card shadow-sm p-4"><div class="d-flex justify-content-between"><div><h2 class="h5 mb-1">{{ trek.name }}</h2><div class="text-secondary">{{ trek.location }} · {{ trek.start_date }} → {{ trek.end_date }}</div></div><StatusBadge :status="trek.status" /></div><div class="row g-2 mt-3"><div class="col-6"><label class="form-label">Available slots</label><input :value="trek.available_slots" type="number" min="0" :max="trek.capacity" class="form-control" @change="update(trek.id,{available_slots:Number($event.target.value)})"></div><div class="col-6"><label class="form-label">Status</label><select :value="trek.status" class="form-select" @change="update(trek.id,{status:$event.target.value})"><option v-if="trek.status==='APPROVED'">APPROVED</option><option v-if="trek.status==='OPEN'">OPEN</option><option v-if="trek.status==='OPEN'||trek.status==='CLOSED'">CLOSED</option><option v-if="trek.status==='CLOSED'">COMPLETED</option></select></div></div><div class="mt-3 d-flex gap-2"><button v-if="trek.status==='OPEN'" class="btn btn-outline-dark" @click="start(trek.id)">Mark started</button><button v-if="trek.status==='CLOSED'" class="btn btn-dark" @click="complete(trek.id)">Mark completed</button><router-link class="btn btn-outline-secondary" :to="`/staff/participants/${trek.id}`">Participants</router-link></div></div></div></div>
</template>
