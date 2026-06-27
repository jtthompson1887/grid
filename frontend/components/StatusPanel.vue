<template lang="pug">
dl
  dt
    | Time
    HelpButton(
      v-if="showHelp"
      help="<p>Data for power generation (except for solar power) is updated every five minutes. Data for solar power and energy transfers is updated every thirty minutes.</p>"
      label="Time"
      @show="$emit('showHelp', $event)"
    )
  dd
    time(:datetime="timeFormatted.datetime") {{ timeFormatted.display }}
      abbr {{ timeFormatted.ampm }}
  dt
    | Price
    HelpButton(
      v-if="showHelp"
      help="<p>As a market-traded commodity, electricity doesn't have just one price: buyers and sellers can enter into contracts hours, days, weeks, or months in advance. This site shows the price on the APX spot market, which reflects the real-time wholesale price of electricity in Great Britain.</p><p>During periods of low demand and high renewable power generation, prices can fall below zero due to the <a href='https://www.gov.uk/government/publications/contracts-for-difference/contract-for-difference'>Contracts For Difference scheme</a>. However, the structure of the British electricity market means that <a href='https://www.carbonbrief.org/factcheck-why-expensive-gas-not-net-zero-is-keeping-uk-electricity-prices-so-high/'>electricity prices are set by the price of gas 98% of the time</a>. Soaring gas prices following Russia's invasion of Ukraine have caused household electricity bills to more than double, leading to a cost-of-living crisis.</p>"
      label="Price"
      @show="$emit('showHelp', $event)"
    )
  dd {{ formatPrice(datum.price.price || 0) }}
    abbr /MWh
  dt
    | Emissions
    HelpButton(
      v-if="showHelp"
      help="<p>The burning of coal, gas, and biomass produces carbon dioxide. The increase in atmospheric carbon dioxide from around 280 parts per million before the industrial revolution to over 400 parts per million today has resulted in a climate crisis, as increased global average temperatures cause progressively more extreme weather.</p><p>The National Oceanic And Atmospheric Administration has been tracking <a href='https://gml.noaa.gov/ccgg/trends/mlo.html'>levels of atmospheric carbon dioxide</a> since 1958.</p>"
      label="Emissions"
      @show="$emit('showHelp', $event)"
    )
  dd {{ Math.round(datum.emissions.emissions || 0) }}
    abbr g/kWh
</template>

<script setup lang="ts">
import type { DatumData } from '~/types/grid'

const props = defineProps<{
  datum: DatumData
  time: number
  showHelp?: boolean
}>()

defineEmits<{
  showHelp: [help: string, label: string]
}>()

const { formatPrice, formatTime } = useFormatters()

const timeFormatted = computed(() => formatTime(props.time))
</script>
