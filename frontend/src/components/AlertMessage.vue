<template>
  <div v-if="message" class="alert" :class="type === 'success' ? 'alert-success' : 'alert-danger'">{{ message }}</div>
</template>

<script setup>
defineProps({ message: String, type: { type: String, default: 'danger' } })
</script>
