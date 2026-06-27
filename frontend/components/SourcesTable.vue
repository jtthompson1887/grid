<template lang="pug">
table.sources(:class="{ transfers: isTransfers }")
  tbody
    tr(v-for="row in rows" :key="row.key")
      td(:class="row.key")
      td
        | {{ row.label }}
        | &nbsp;
        HelpButton(
          v-if="row.help"
          :help="row.help"
          :label="row.label"
          @show="$emit('showHelp', $event)"
        )
      td {{ row.isDash ? '—' : formatPower(row.value) }}
      td {{ row.isDash ? '—' : formatPercentage(row.value / demand) }}
</template>

<script setup lang="ts">
const props = defineProps<{
  mapData: Record<string, number>
  keys: Array<{ key: string; label: string; help: string; isDash?: boolean }>
  demand: number
  isTransfers?: boolean
}>()

defineEmits<{
  showHelp: [help: string, label: string]
}>()

const { formatPower, formatPercentage } = useFormatters()

const rows = computed(() =>
  props.keys.map(k => ({
    ...k,
    value: props.mapData[k.key] || 0,
  }))
)
</script>
