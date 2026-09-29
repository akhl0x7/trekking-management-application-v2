<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import StatusBadge from '../../components/StatusBadge.vue'
import AlertMessage from '../../components/AlertMessage.vue'

const treks = ref([])
const showForm = ref(false)
const error = ref('')
const message = ref('')
const search = ref('')
const editing = ref(null)
const form = ref({ name: '', location: '', difficulty: 'EASY', duration_days: 1, capacity: 10, available_slots: 10, start_date: '', end_date: '', price: 0, description: '', instructions: '' })

function reset() {
  editing.value = null
  showForm.value = false
  form.value = { name: '', location: '', difficulty: 'EASY', duration_days: 1, capacity: 10, available_slots: 10, start_date: '', end_date: '', price: 0, description: '', instructions: '' }
}

async function load() {
  try { treks.value = await api(`/admin/treks${search.value ? `?search=${encodeURIComponent(search.value)}` : ''}`); error.value = '' } catch (e) { error.value = e.message }
}

function newForm() {
  editing.value = null
  form.value = { name: '', location: '', difficulty: 'EASY', duration_days: 1, capacity: 10, available_slots: 10, start_date: '', end_date: '', price: 0, description: '', instructions: '' }
  showForm.value = true
}

function edit(trek) {
  editing.value = trek.id
  showForm.value = true
  form.value = { name: trek.name, location: trek.location, difficulty: trek.difficulty, duration_days: trek.duration_days, capacity: trek.capacity, available_slots: trek.available_slots, start_date: trek.start_date, end_date: trek.end_date, price: trek.price, description: trek.description, instructions: trek.instructions }
}

async function save() {
  try {
    const result = editing.value ? await api(`/admin/treks/${editing.value}`, { method: 'PATCH', body: JSON.stringify(form.value) }) : await api('/admin/treks', { method: 'POST', body: JSON.stringify(form.value) })
    message.value = editing.value ? 'Trek updated.' : 'Trek created.'
    reset()
    await load()
    return result
  } catch (e) { error.value = e.message }
}

async function approve(id) { try { await api(`/admin/treks/${id}/approve`, { method: 'POST' }); message.value = 'Trek approved.'; await load() } catch (e) { error.value = e.message } }
async function remove(id) { if (!confirm('Delete this trek?')) return; try { await api(`/admin/treks/${id}`, { method: 'DELETE' }); message.value = 'Trek deleted.'; await load() } catch (e) { error.value = e.message } }

onMounted(load)
</script>

<template>
  <PageHeader title="Trek management" subtitle="Create, review and maintain trekking events."><button class="btn btn-dark" @click="newForm">New trek</button></PageHeader>
  <AlertMessage :message="error" /><AlertMessage :message="message" type="success" />
  <div class="card shadow-sm p-4 mb-4">
    <div class="input-group"><input v-model="search" class="form-control" placeholder="Search by name or location" @keyup.enter="load"><button class="btn btn-outline-dark" @click="load">Search</button></div>
  </div>
  <div v-if="showForm" class="card shadow-sm p-4 mb-4">
    <h2 class="h5">{{ editing ? 'Edit trek' : 'Create trek' }}</h2>
    <form @submit.prevent="save" class="row g-3">
      <div class="col-md-6"><label class="form-label">Name</label><input v-model="form.name" class="form-control" required></div>
      <div class="col-md-6"><label class="form-label">Location</label><input v-model="form.location" class="form-control" required></div>
      <div class="col-md-3"><label class="form-label">Difficulty</label><select v-model="form.difficulty" class="form-select"><option>EASY</option><option>MODERATE</option><option>HARD</option></select></div>
      <div class="col-md-3"><label class="form-label">Duration (days)</label><input v-model.number="form.duration_days" type="number" min="1" class="form-control" required></div>
      <div class="col-md-3"><label class="form-label">Capacity</label><input v-model.number="form.capacity" type="number" min="1" class="form-control" required></div><div class="col-md-3"><label class="form-label">Available slots</label><input v-model.number="form.available_slots" type="number" min="0" class="form-control" required></div>
      <div class="col-md-3"><label class="form-label">Price</label><input v-model.number="form.price" type="number" min="0" step="0.01" class="form-control"></div>
      <div class="col-md-6"><label class="form-label">Start date</label><input v-model="form.start_date" type="date" class="form-control" required></div>
      <div class="col-md-6"><label class="form-label">End date</label><input v-model="form.end_date" type="date" class="form-control" required></div>
      <div class="col-12"><label class="form-label">Description</label><textarea v-model="form.description" class="form-control" rows="2"></textarea></div>
      <div class="col-12"><label class="form-label">Instructions</label><textarea v-model="form.instructions" class="form-control" rows="2"></textarea></div>
      <div class="col-12 d-flex gap-2"><button class="btn btn-dark">Save</button><button type="button" class="btn btn-outline-secondary" @click="reset">Cancel</button></div>
    </form>
  </div>
  <div class="card shadow-sm"><div class="table-responsive"><table class="table align-middle mb-0"><thead><tr><th>Trek</th><th>Dates</th><th>Availability</th><th>Status</th><th></th></tr></thead><tbody><tr v-for="trek in treks" :key="trek.id"><td><strong>{{ trek.name }}</strong><div class="small text-secondary">{{ trek.location }} · {{ trek.difficulty }}</div></td><td>{{ trek.start_date }} → {{ trek.end_date }}</td><td>{{ trek.available_slots }}</td><td><StatusBadge :status="trek.status" /></td><td class="text-end"><button class="btn btn-sm btn-outline-dark me-1" @click="edit(trek)">Edit</button><button v-if="trek.status === 'PENDING'" class="btn btn-sm btn-outline-success me-1" @click="approve(trek.id)">Approve</button><button class="btn btn-sm btn-outline-danger" @click="remove(trek.id)">Delete</button></td></tr></tbody></table></div></div>
</template>
