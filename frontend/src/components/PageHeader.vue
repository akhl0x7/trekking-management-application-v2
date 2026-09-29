<template>
  <div class="d-flex justify-content-between align-items-start gap-3 mb-4">
    <div>
      <h1 class="h3 mb-1"><slot name="title">{{ title }}</slot></h1>
      <p v-if="subtitle" class="text-secondary mb-0">{{ subtitle }}</p>
    </div>
    <div><slot /></div>
  </div>
</template>

<script setup>
defineProps({ title: String, subtitle: String })
</script>
