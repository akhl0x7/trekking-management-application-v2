<template>
  <span class="badge" :class="classes">{{ status }}</span>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ status: String })
const classes = computed(() => ({
  'text-bg-success': ['OPEN', 'ACTIVE', 'BOOKED', 'COMPLETED'].includes(props.status),
  'text-bg-secondary': ['APPROVED', 'CANCELLED', 'INACTIVE'].includes(props.status),
  'text-bg-warning': ['PENDING'].includes(props.status),
  'text-bg-danger': ['BLACKLISTED'].includes(props.status),
  'text-bg-dark': props.status === 'CLOSED'
}))
</script>
