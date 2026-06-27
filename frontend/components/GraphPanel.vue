<template lang="pug">
div.graph(
  :data-prefix="prefix"
  :data-suffix="suffix"
  :data-transfers="graphKey === 'transfers' ? 'true' : undefined"
)
  div
    template(v-for="label in valueAxisLabels" :key="label.value")
      div {{ label.text }}
      div
  div
    div(v-for="t in timeAxisLabels" :key="t") {{ t }}
  svg(
    :viewBox="`0 0 ${SIZE} ${SIZE}`"
    :width="SIZE"
    :height="SIZE"
    preserveAspectRatio="none"
    @mouseover="handleMouseOver"
    @mouseleave="hideKey"
  )
    polyline(
      v-for="(pts, key) in polylines"
      :key="key"
      :class="key"
      :points="pts"
    )
    rect(
      v-for="(rect, i) in overlayRects"
      :key="i"
      :x="rect.x"
      y="0"
      :width="rect.width"
      :height="SIZE"
      :data-time="rect.time"
      :data-values="rect.values"
    )
  div(v-if="keyVisible" ref="keyEl" :style="keyStyle")
    div {{ keyTime }}
    table(:class="'sources' + (graphKey === 'transfers' ? ' transfers' : '')")
      tbody
        tr(v-for="(row, i) in keyRows" :key="i")
          td(:class="row.cls")
          td {{ row.label }}
          td {{ row.value }}
</template>

<script setup lang="ts">
import type { SeriesEntry, AxesData } from '~/types/grid'

const SIZE = 500
const KEY_MARGIN = 8

const LABELS: Record<string, string> = {
  price: 'Price per MWh', emissions: 'Emissions per kWh', demand: 'Demand',
  generation: 'Generation', fossils: 'Fossil fuels', renewables: 'Renewables',
  others: 'Other sources', transfers: 'Transfers', coal: 'Coal', gas: 'Gas',
  solar: 'Solar', wind: 'Wind', hydro: 'Hydroelectric', nuclear: 'Nuclear',
  biomass: 'Biomass', belgium: 'Belgium', denmark: 'Denmark', france: 'France',
  ireland: 'Ireland', netherlands: 'Netherlands', norway: 'Norway', pumped: 'Pumped storage',
}

type GraphKey = 'price' | 'emissions' | 'generation' | 'transfers' | 'demand' | 'visits'

const props = defineProps<{
  series: SeriesEntry[]
  axes: AxesData
  graphKey: GraphKey
  prefix: string
  suffix: string
  timeStep: number
  timeFormat: string
  decimalPlaces: number
}>()

const { formatDate } = useFormatters()
const { getPoints } = useGraphPoints()

function getMapKeys(entry: SeriesEntry): string[] {
  return Object.keys(entry.datum[props.graphKey as keyof typeof entry.datum] as object)
}

function getMapValues(entry: SeriesEntry): number[] {
  return Object.values(entry.datum[props.graphKey as keyof typeof entry.datum] as object) as number[]
}

const minimum = computed(() => props.axes.minimum)
const maximum = computed(() => props.axes.maximum)
const range = computed(() => maximum.value - minimum.value)
const step = computed(() => props.axes.step)

const valueAxisLabels = computed(() => {
  const labels = []
  for (let v = maximum.value; v >= minimum.value; v -= step.value) {
    const neg = v < 0
    const text = (neg ? '−' : '') + props.prefix + Math.abs(v).toLocaleString() + props.suffix
    labels.push({ value: v, text })
  }
  return labels
})

const timeAxisLabels = computed(() => {
  const labels: string[] = []
  let index = Math.ceil(props.timeStep / 2)
  props.series.forEach(entry => {
    if (index % props.timeStep === 0) {
      labels.push(formatDate(entry.time, props.timeFormat))
    }
    index++
  })
  return labels
})

const polylines = computed(() => {
  if (!props.series.length) return {}
  const keys = getMapKeys(props.series[0])
  const result: Record<string, string> = {}
  for (const key of keys) {
    const values = props.series.map(e => (e.datum[props.graphKey as keyof typeof e.datum] as Record<string, number>)[key] || 0)
    result[key] = getPoints(values, minimum.value, range.value)
  }
  return result
})

const overlayRects = computed(() => {
  const count = props.series.length
  if (!count) return []
  return props.series.map((entry, index) => {
    const vals = getMapValues(entry)
    return {
      x: Math.round(SIZE * index / count),
      width: Math.round(SIZE / count),
      time: formatDate(entry.time, props.timeFormat),
      values: vals.map(v => {
        const neg = v < 0
        return (neg ? '-' : '') + Math.abs(v).toFixed(props.decimalPlaces)
      }).join(' '),
    }
  })
})

const keyVisible = ref(false)
const keyTime = ref('')
const keyRows = ref<Array<{ cls: string; label: string; value: string }>>([])
const keyStyle = ref('')
const keyEl = ref<HTMLElement | null>(null)

function handleMouseOver(e: MouseEvent) {
  const target = e.target as SVGRectElement
  if (target.nodeName !== 'rect') return

  const rawValues = target.dataset.values?.split(' ') || []
  const keys = props.series.length ? getMapKeys(props.series[0]) : []

  keyTime.value = target.dataset.time || ''
  keyRows.value = keys.map((key, i) => {
    const raw = rawValues[i] || '0'
    const neg = raw.startsWith('-')
    const display = (neg ? '−' : '') + props.prefix + raw.replace('-', '') + props.suffix
    return { cls: key, label: LABELS[key] || key, value: display }
  })
  keyVisible.value = true

  nextTick(() => {
    if (!keyEl.value) return
    const keyWidth = keyEl.value.offsetWidth
    const svgEl = (e.target as Element).closest('svg')
    if (!svgEl) return
    const rectBounds = target.getBoundingClientRect()
    const svgBounds = svgEl.getBoundingClientRect()
    let left = rectBounds.left - svgBounds.left

    if (rectBounds.left > keyWidth + 2 * KEY_MARGIN) {
      left -= keyWidth + KEY_MARGIN
    } else {
      left += rectBounds.width + KEY_MARGIN
    }
    keyStyle.value = `left: ${left}px`
  })
}

function hideKey() {
  keyVisible.value = false
}
</script>
