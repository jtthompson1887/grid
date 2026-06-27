<template lang="pug">
section#transition
  h2 The energy transition
  p
    | Between 12th January 1882, when the world's first coal-fired power station opened at 57 Holborn Viaduct in London, and 30th September 2024, when Great Britain's last coal-fired power station closed, the country burnt 4.6 billion tonnes of coal, #[a(href="https://interactive.carbonbrief.org/coal-phaseout-UK/") emitting 10.6 billion tonnes of carbon dioxide].
  p
    | In 2001 the European Union updated the Large Combustion Plant Directive, obliging power stations to limit their emissions or close by 2015. Most older coal-fired power stations in Great Britain closed in response. The government's introduction of a carbon price floor in 2013, and its subsequent increase in 2015, made coal uncompetitive with gas, which rapidly replaced coal in the country's energy mix.
  p
    | At the same time, renewable power generation was steadily rising. Great Britain's exposed position in the north-east Atlantic makes it one of the best locations in the world for wind power, and the shallow waters of the North Sea host several of the world's largest offshore wind farms.
  p
    | New wind power records are set regularly, and between {{ recordStartTime }} and {{ recordEndTime }} on {{ recordDate }} British wind farms averaged a record {{ formatPower(state.wind_record.power) }}GW of generation.
  table.wind-milestones
    tr
      th Power
      th Date first achieved
    tr(v-for="m in state.wind_milestones" :key="m.power")
      td {{ m.power }}
        abbr GW
      td {{ formatDate(m.time, 'jS F Y') }}
</template>

<script setup lang="ts">
import type { GridState } from '~/types/grid'

const props = defineProps<{
  state: GridState
}>()

const { formatPower, formatDate } = useFormatters()

const recordStartTime = computed(() => formatDate(props.state.wind_record.time, 'g:ia'))
const recordEndTime = computed(() => formatDate(props.state.wind_record.time + 1800, 'g:ia'))
const recordDate = computed(() => formatDate(props.state.wind_record.time, 'jS F Y'))
</script>
