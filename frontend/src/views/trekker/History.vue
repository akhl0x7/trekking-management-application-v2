<script setup>
import { onMounted, ref, onUnmounted } from 'vue'
import { api } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import StatusBadge from '../../components/StatusBadge.vue'
const history=ref([]),job=ref(null),error=ref(''),message=ref(''),timer=ref(null)
async function load(){try{history.value=await api('/trekker/history')}catch(e){error.value=e.message}}
async function startExport(){try{job.value=await api('/trekker/exports',{method:'POST'});message.value='Export queued.';timer.value=setInterval(checkExport,1500)}catch(e){error.value=e.message}}
async function checkExport(){if(!job.value)return;try{job.value=await api(`/trekker/exports/${job.value.id}`);if(job.value.status==='COMPLETED'){clearInterval(timer.value);timer.value=null;message.value='Export ready.'}}catch(e){clearInterval(timer.value);timer.value=null;error.value=e.message}}
onMounted(load);onUnmounted(()=>{if(timer.value)clearInterval(timer.value)})
</script>
<template><PageHeader title="Trekking history" subtitle="Your complete booking history."><button class="btn btn-dark" @click="startExport">Export CSV</button></PageHeader><div v-if="error" class="alert alert-danger">{{ error }}</div><div v-if="message" class="alert alert-success">{{ message }} <a v-if="job?.status==='COMPLETED'" class="alert-link ms-2" :href="job.file">Download</a></div><div v-if="job && job.status!=='COMPLETED'" class="small text-secondary mb-3">Export status: {{ job.status }}</div><div class="card shadow-sm"><div class="table-responsive"><table class="table align-middle mb-0"><thead><tr><th>Trek</th><th>Location</th><th>Dates</th><th>Status</th></tr></thead><tbody><tr v-for="b in history" :key="b.id"><td>{{ b.trek_name }}</td><td>{{ b.location }}</td><td>{{ b.start_date }} → {{ b.end_date }}</td><td><StatusBadge :status="b.status" /></td></tr></tbody></table></div></div></template>
