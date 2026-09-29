<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
const form=ref({name:'',phone:'',emergency_contact:''}),error=ref(''),message=ref('')
async function load(){try{const data=await api('/trekker/profile');form.value={name:data.name,phone:data.profile?.phone||'',emergency_contact:data.profile?.emergency_contact||''}}catch(e){error.value=e.message}}
async function save(){try{await api('/trekker/profile',{method:'PATCH',body:JSON.stringify(form.value)});message.value='Profile updated.'}catch(e){error.value=e.message}}
onMounted(load)
</script>
<template><PageHeader title="Profile" subtitle="Keep participant contact information current."/><div v-if="error" class="alert alert-danger">{{ error }}</div><div v-if="message" class="alert alert-success">{{ message }}</div><div class="card shadow-sm p-4 col-lg-7"><form @submit.prevent="save"><div class="mb-3"><label class="form-label">Name</label><input v-model="form.name" class="form-control" required></div><div class="mb-3"><label class="form-label">Phone</label><input v-model="form.phone" class="form-control"></div><div class="mb-3"><label class="form-label">Emergency contact</label><input v-model="form.emergency_contact" class="form-control"></div><button class="btn btn-dark">Save changes</button></form></div></template>
