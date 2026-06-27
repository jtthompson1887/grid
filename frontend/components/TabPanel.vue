<template lang="pug">
div
  div
    StatusPanel(:datum="datum" :time="time" @showHelp="$emit('showHelp', $event)")
  div
    EquationPanel(:datum="datum" @showHelp="$emit('showHelp', $event)")
  div
    div.pie-chart-container
      PieChart(:datum="datum")
  div
    h3 Generation by type
    table.sources
      tbody
        tr(v-for="(label, key) in typeKeys" :key="key")
          td(:class="key")
          td {{ label }}
          td {{ formatTotalPower(datum.types[key] || 0) }}
          td {{ formatPercentage((datum.types[key] || 0) / demand) }}
    h3 Generation by source
    table.sources
      tbody
        tr(v-for="(label, key) in generationKeys" :key="key")
          td(:class="key")
          td {{ label }}
          td {{ formatPower(datum.generation[key] || 0) }}
          td {{ formatPercentage((datum.generation[key] || 0) / demand) }}
    h3 Interconnectors
    table.sources.transfers
      tbody
        tr(v-for="(label, key) in interconnectorKeys" :key="key")
          td(:class="key")
          td {{ label }}
          td {{ formatPower(datum.interconnectors[key] || 0) }}
          td {{ formatPercentage((datum.interconnectors[key] || 0) / demand) }}
    h3 Storage
    table.sources.transfers
      tbody
        tr(v-for="(label, key) in storageKeys" :key="key")
          td(:class="key")
          td {{ label }}
          td {{ formatPower(datum.storage[key] || 0) }}
          td {{ formatPercentage((datum.storage[key] || 0) / demand) }}
  div
    h3 Price per MWh
    GraphPanel(
      :series="series"
      :axes="axes.price"
      graphKey="price"
      prefix="£"
      suffix=""
      :timeStep="timeStep"
      :timeFormat="timeFormat"
      :decimalPlaces="2"
    )
  div
    h3 Emissions per kWh
    GraphPanel(
      :series="series"
      :axes="axes.emissions"
      graphKey="emissions"
      prefix=""
      suffix="g"
      :timeStep="timeStep"
      :timeFormat="timeFormat"
      :decimalPlaces="0"
    )
  div
    h3 Demand
    GraphPanel(
      :series="series"
      :axes="axes.demand"
      graphKey="demand"
      prefix=""
      suffix="GW"
      :timeStep="timeStep"
      :timeFormat="timeFormat"
      :decimalPlaces="1"
    )
  div
    h3 Generation
    GraphPanel(
      :series="series"
      :axes="axes.generation"
      graphKey="generation"
      prefix=""
      suffix="GW"
      :timeStep="timeStep"
      :timeFormat="timeFormat"
      :decimalPlaces="2"
    )
  div
    h3 Transfers
    GraphPanel(
      :series="series"
      :axes="axes.transfers"
      graphKey="transfers"
      prefix=""
      suffix="GW"
      :timeStep="timeStep"
      :timeFormat="timeFormat"
      :decimalPlaces="2"
    )
</template>

<script setup lang="ts">
import type { DatumData, SeriesEntry, AllAxes } from '~/types/grid'

const props = defineProps<{
  datum: DatumData
  time: number
  series: SeriesEntry[]
  axes: AllAxes
  timeStep: number
  timeFormat: string
}>()

defineEmits<{
  showHelp: [help: string, label: string]
}>()

const { formatPower, formatTotalPower, formatPercentage } = useFormatters()

const demand = computed(() => props.datum.total || 1)

const typeKeys: Record<string, string> = {
  fossils: 'Fossil fuels', renewables: 'Renewables', others: 'Other sources'
}

const generationKeys: Record<string, string> = {
  coal: 'Coal', gas: 'Gas', solar: 'Solar', wind: 'Wind',
  hydro: 'Hydroelectric', nuclear: 'Nuclear', biomass: 'Biomass'
}

const interconnectorKeys: Record<string, string> = {
  belgium: 'Belgium', denmark: 'Denmark', france: 'France',
  ireland: 'Ireland', netherlands: 'Netherlands', norway: 'Norway'
}

const storageKeys: Record<string, string> = {
  pumped: 'Pumped storage'
}
</script>
