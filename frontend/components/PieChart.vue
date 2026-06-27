<template lang="pug">
div.pie-chart
  div
    div Generation
    div(:class="activeSource")
    div
      span {{ activePower }}
      | GW
    div
      span {{ activePercentage }}
      | %
  svg(
    viewBox="-1 -1 2 2"
    :data-power="generationPower"
    :data-percentage="generationPercentage"
    @mouseover="handleMouseOver"
    @mouseout="handleMouseOut"
  )
    path(
      v-for="arc in outerArcs"
      :key="arc.key"
      :class="arc.key"
      :d="arc.d"
      :data-power="arc.power"
      :data-percentage="arc.percentage"
    )
    path(
      v-for="arc in innerArcs"
      :key="'inner-' + arc.key"
      :class="arc.key"
      :d="arc.d"
      :data-power="arc.power"
      :data-percentage="arc.percentage"
    )
</template>

<script setup lang="ts">
import type { DatumData } from '~/types/grid'

const OUTER_RADIUS = 0.75
const INNER_RADIUS = 0.50

const GENERATION_KEYS = ['coal', 'gas', 'solar', 'wind', 'hydro', 'nuclear', 'biomass']
const TYPE_KEYS = ['fossils', 'renewables', 'others']

const props = defineProps<{
  datum: DatumData
}>()

const { formatPower, formatTotalPower, formatPercentage } = useFormatters()

const activeSource = ref('generation')
const activePower = ref('')
const activePercentage = ref('')

const totalGeneration = computed(() => {
  return Object.values(props.datum.generation).reduce((a, b) => a + b, 0)
})
const totalDemand = computed(() => props.datum.total || 1)

const generationPower = computed(() => formatTotalPower(
  (props.datum.demand.fossils || 0) + (props.datum.demand.renewables || 0) + (props.datum.demand.others || 0)
))
const generationPercentage = computed(() => formatPercentage(totalGeneration.value / totalDemand.value))

function arcPath(offset: number, fraction: number, innerRadius: number, outerRadius: number): string {
  const startOuter = arcPoint(offset, outerRadius)
  const endOuter = arcPoint(offset + fraction, outerRadius)
  const startInner = arcPoint(offset + fraction, innerRadius)
  const endInner = arcPoint(offset, innerRadius)
  const large = fraction >= 0.5 ? 1 : 0
  return (
    `M${startOuter}A${outerRadius},${outerRadius} 0 ${large} 1 ${endOuter}` +
    `L${startInner}A${innerRadius},${innerRadius} 0 ${large} 0 ${endInner}z`
  )
}

function arcPoint(fraction: number, radius: number): string {
  const x = (radius * Math.sin(fraction * 2 * Math.PI)).toFixed(4)
  const y = (radius * -Math.cos(fraction * 2 * Math.PI)).toFixed(4)
  return `${x},${y}`
}

function buildArcs(keys: string[], mapData: Record<string, number>, isTotal: boolean) {
  const arcs = []
  let offset = 0
  const gen = totalGeneration.value || 1
  const demand = totalDemand.value || 1

  for (const key of keys) {
    const power = mapData[key] || 0
    if (power > 0) {
      const fraction = power / gen
      arcs.push({
        key,
        d: arcPath(offset, fraction, INNER_RADIUS, OUTER_RADIUS),
        power: isTotal ? formatTotalPower(power) : formatPower(power),
        percentage: formatPercentage(power / demand),
      })
      offset += fraction
    }
  }
  return arcs
}

const outerArcs = computed(() => buildArcs(GENERATION_KEYS, props.datum.generation, false))
const innerArcs = computed(() => buildArcs(TYPE_KEYS, props.datum.types, true))

function handleMouseOver(e: MouseEvent) {
  const target = e.target as SVGPathElement
  if (target.nodeName === 'path') {
    const source = target.getAttribute('class') || 'generation'
    activeSource.value = source
    const srcEl = target
    activePower.value = srcEl.dataset.power || generationPower.value
    activePercentage.value = srcEl.dataset.percentage || generationPercentage.value
  }
}

function handleMouseOut(e: MouseEvent) {
  const target = e.target as SVGPathElement
  if (target.nodeName === 'path') {
    activeSource.value = 'generation'
    activePower.value = generationPower.value
    activePercentage.value = generationPercentage.value
  }
}

onMounted(() => {
  activePower.value = generationPower.value
  activePercentage.value = generationPercentage.value
})

watch([generationPower, generationPercentage], () => {
  if (activeSource.value === 'generation') {
    activePower.value = generationPower.value
    activePercentage.value = generationPercentage.value
  }
})
</script>
