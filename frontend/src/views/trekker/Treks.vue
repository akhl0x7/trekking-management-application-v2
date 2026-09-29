<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import StatusBadge from '../../components/StatusBadge.vue'

const treks=ref([]),selected=ref(null),error=ref(''),message=ref('')
const filters=ref({search:'',difficulty:'',location:'',duration:''})
async function load(){try{const params=new URLSearchParams();Object.entries(filters.value).forEach(([key,value])=>{if(value)params.set(key,value)});treks.value=await api(`/treks${params.toString()?`?${params}`:''}`);error.value=''}catch(e){error.value=e.message}}
async function book(id){try{await api(`/trekker/treks/${id}/book`,{method:'POST'});message.value='Booking confirmed.';await load();if(selected.value)selected.value=treks.value.find(t=>t.id===id)||selected.value}catch(e){error.value=e.message}}
onMounted(load)
</script>
<template>
  <PageHeader title="Browse treks" subtitle="Search and filter open and approved trekking events."><button class="btn btn-outline-dark" @click="load">Refresh</button></PageHeader>
  <div v-if="error" class="alert alert-danger">{{ error }}</div><div v-if="message" class="alert alert-success">{{ message }}</div>
  <div class="card shadow-sm p-4 mb-4"><div class="row g-2"><div class="col-lg-4"><input v-model="filters.search" class="form-control" placeholder="Search name or location" @keyup.enter="load"></div><div class="col-lg-2"><select v-model="filters.difficulty" class="form-select"><option value="">Difficulty</option><option>EASY</option><option>MODERATE</option><option>HARD</option></select></div><div class="col-lg-3"><input v-model="filters.location" class="form-control" placeholder="Location"></div><div class="col-lg-2"><input v-model="filters.duration" type="number" min="1" class="form-control" placeholder="Days"></div><div class="col-lg-1"><button class="btn btn-dark w-100" @click="load">Go</button></div></div></div>
  <div class="row g-3"><div v-for="trek in treks" :key="trek.id" class="col-md-6 col-xl-4"><div class="card shadow-sm h-100"><div class="card-body"><div class="d-flex justify-content-between"><span class="small text-secondary">{{ trek.location }} · {{ trek.duration_days }} day(s)</span><StatusBadge :status="trek.status" /></div><h2 class="h5 mt-2">{{ trek.name }}</h2><div class="small text-secondary">{{ trek.difficulty }} · ₹{{ trek.price }}</div><p class="small mt-3">{{ trek.description }}</p><div class="d-flex justify-content-between align-items-center"><span class="small">{{ trek.available_slots }} places available</span><button class="btn btn-dark btn-sm" :disabled="trek.status!=='OPEN'||trek.available_slots<1" @click="book(trek.id)">{{ trek.status==='OPEN'?'Book':'Not bookable' }}</button></div></div></div></div></div>
  <div v-if="!treks.length" class="text-secondary py-4">No treks match the selected filters.</div>
</template>
