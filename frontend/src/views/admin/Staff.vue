<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import StatusBadge from '../../components/StatusBadge.vue'
import AlertMessage from '../../components/AlertMessage.vue'

const staff = ref([])
const treks = ref([])
const form = ref({ name: '', email: '', password: 'Staff@12345', employee_id: '', phone: '', department: '' })
const search = ref('')
const error = ref('')
const message = ref('')

async function load() {
  try { staff.value = await api(`/admin/staff${search.value ? `?search=${encodeURIComponent(search.value)}` : ''}`); treks.value = await api('/admin/treks'); error.value = '' } catch (e) { error.value = e.message }
}
async function create() { try { await api('/admin/staff', { method: 'POST', body: JSON.stringify(form.value) }); message.value = 'Staff account created.'; form.value = { name: '', email: '', password: 'Staff@12345', employee_id: '', phone: '', department: '' }; await load() } catch (e) { error.value = e.message } }
async function updateStatus(user, status) { try { await api(`/admin/staff/${user.id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) }); await load() } catch (e) { error.value = e.message } }
async function assign(trek, staffMember) { try { await api(`/admin/treks/${trek.id}/assign`, { method: 'POST', body: JSON.stringify({ staff_id: staffMember.staff_profile.id }) }); message.value = 'Staff assigned.'; await load() } catch (e) { error.value = e.message } }
async function unassign(trek, staffMember) { try { await api(`/admin/treks/${trek.id}/unassign`, { method: 'POST', body: JSON.stringify({ staff_id: staffMember.staff_profile.id }) }); message.value = 'Staff unassigned.'; await load() } catch (e) { error.value = e.message } }

onMounted(load)
</script>

<template>
  <PageHeader title="Staff management" subtitle="Provision staff accounts and manage trek assignments." />
  <AlertMessage :message="error" /><AlertMessage :message="message" type="success" />
  <div class="row g-4">
    <div class="col-lg-5"><div class="card shadow-sm p-4"><h2 class="h5">Add staff</h2><form @submit.prevent="create" class="row g-3"><div class="col-12"><input v-model="form.name" class="form-control" placeholder="Name" required></div><div class="col-12"><input v-model="form.email" type="email" class="form-control" placeholder="Email" required></div><div class="col-md-6"><input v-model="form.password" type="password" class="form-control" placeholder="Password" required></div><div class="col-md-6"><input v-model="form.employee_id" class="form-control" placeholder="Employee ID" required></div><div class="col-md-6"><input v-model="form.phone" class="form-control" placeholder="Phone"></div><div class="col-md-6"><input v-model="form.department" class="form-control" placeholder="Department"></div><div class="col-12"><button class="btn btn-dark">Create staff</button></div></form></div></div>
    <div class="col-lg-7"><div class="card shadow-sm p-4"><div class="input-group mb-3"><input v-model="search" class="form-control" placeholder="Search staff" @keyup.enter="load"><button class="btn btn-outline-dark" @click="load">Search</button></div><div v-for="member in staff" :key="member.id" class="border rounded p-3 mb-2"><div class="d-flex justify-content-between align-items-start"><div><strong>{{ member.name }}</strong><div class="small text-secondary">{{ member.email }} · {{ member.staff_profile?.employee_id }}</div></div><StatusBadge :status="member.status" /></div><div class="mt-2"><button v-if="member.status === 'ACTIVE'" class="btn btn-sm btn-outline-warning" @click="updateStatus(member, 'INACTIVE')">Deactivate</button><button v-else class="btn btn-sm btn-outline-success" @click="updateStatus(member, 'ACTIVE')">Activate</button><button class="btn btn-sm btn-outline-danger ms-2" @click="updateStatus(member, 'BLACKLISTED')">Blacklist</button></div></div></div></div>
  </div>
  <div class="card shadow-sm p-4 mt-4"><h2 class="h5">Assignments</h2><div v-for="trek in treks" :key="trek.id" class="border rounded p-3 mb-2"><div class="d-flex justify-content-between"><strong>{{ trek.name }}</strong><StatusBadge :status="trek.status" /></div><div class="small text-secondary mb-2">Current assignments: {{ trek.staff.length }}</div><div class="d-flex flex-wrap gap-2"><span v-for="member in staff" :key="member.id" class="btn-group"><button class="btn btn-sm btn-outline-dark" @click="assign(trek, member)">{{ member.name }}</button><button v-if="trek.staff.some(s => s.staff_id === member.staff_profile?.id)" class="btn btn-sm btn-outline-danger" @click="unassign(trek, member)">×</button></span></div></div></div>
</template>
