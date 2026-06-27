<template lang="pug">
span(
  :data-help="help"
  @click="$emit('show', help, label)"
)
</template>

<script setup lang="ts">
defineProps<{
  help: string
  label: string
}>()
defineEmits<{
  show: [help: string, label: string]
}>()
</script>
