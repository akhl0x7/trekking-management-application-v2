<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import StatusBadge from '../../components/StatusBadge.vue'

const users = ref([])
const search = ref('')
const error = ref('')
async function load() { try { users.value = await api(`/admin/users${search.value ? `?search=${encodeURIComponent(search.value)}` : ''}`); error.value = '' } catch (e) { error.value = e.message } }
async function status(user, value) { try { await api(`/admin/users/${user.id}/status`, { method: 'PATCH', body: JSON.stringify({ status: value }) }); await load() } catch (e) { error.value = e.message } }
onMounted(load)
</script>

<template>
  <PageHeader title="Trekker management" subtitle="Search and manage registered participants." />
  <div v-if="error" class="alert alert-danger">{{ error }}</div>
  <div class="card shadow-sm p-4 mb-3"><div class="input-group"><input v-model="search" class="form-control" placeholder="Search users" @keyup.enter="load"><button class="btn btn-outline-dark" @click="load">Search</button></div></div>
  <div class="card shadow-sm"><div class="table-responsive"><table class="table align-middle mb-0"><thead><tr><th>Name</th><th>Email</th><th>Status</th><th></th></tr></thead><tbody><tr v-for="user in users" :key="user.id"><td>{{ user.name }}</td><td>{{ user.email }}</td><td><StatusBadge :status="user.status" /></td><td class="text-end"><button v-if="user.status === 'ACTIVE'" class="btn btn-sm btn-outline-warning" @click="status(user, 'INACTIVE')">Deactivate</button><button v-else class="btn btn-sm btn-outline-success" @click="status(user, 'ACTIVE')">Activate</button><button class="btn btn-sm btn-outline-danger ms-2" @click="status(user, 'BLACKLISTED')">Blacklist</button></td></tr></tbody></table></div></div>
</template>
