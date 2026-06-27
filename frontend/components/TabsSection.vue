<template lang="pug">
section
  div(role="tablist")
    h2#tab-day(
      role="tab"
      aria-controls="tab-panel-day"
      :aria-selected="activeTab === 'day' ? 'true' : 'false'"
      :tabindex="activeTab === 'day' ? 0 : -1"
      @click="selectTab('day')"
      @keydown="handleKeyDown"
    )
      span Past&nbsp;
      | day
    h2#tab-week(
      role="tab"
      aria-controls="tab-panel-week"
      :aria-selected="activeTab === 'week' ? 'true' : 'false'"
      :tabindex="activeTab === 'week' ? 0 : -1"
      @click="selectTab('week')"
      @keydown="handleKeyDown"
    )
      span Past&nbsp;
      | week
    h2#tab-year(
      role="tab"
      aria-controls="tab-panel-year"
      :aria-selected="activeTab === 'year' ? 'true' : 'false'"
      :tabindex="activeTab === 'year' ? 0 : -1"
      @click="selectTab('year')"
      @keydown="handleKeyDown"
    )
      span Past&nbsp;
      | year
    h2#tab-all(
      role="tab"
      aria-controls="tab-panel-all"
      :aria-selected="activeTab === 'all' ? 'true' : 'false'"
      :tabindex="activeTab === 'all' ? 0 : -1"
      @click="selectTab('all')"
      @keydown="handleKeyDown"
    )
      | All
      span &nbsp;time

  div#tab-panel-day(
    role="tabpanel"
    aria-labelledby="tab-day"
    tabindex="0"
    :style="activeTab === 'day' ? 'display:grid' : 'display:none'"
  )
    TabPanel(
      :datum="state.past_day"
      :time="state.time"
      :series="state.past_day_series"
      :axes="axes"
      :timeStep="12"
      timeFormat="g:ia"
      @showHelp="$emit('showHelp', $event)"
    )

  div#tab-panel-week(
    role="tabpanel"
    aria-labelledby="tab-week"
    tabindex="0"
    :style="activeTab === 'week' ? 'display:grid' : 'display:none'"
  )
    TabPanel(
      :datum="state.past_week"
      :time="state.time"
      :series="state.past_week_series"
      :axes="axes"
      :timeStep="1"
      timeFormat="l"
      @showHelp="$emit('showHelp', $event)"
    )

  div#tab-panel-year(
    role="tabpanel"
    aria-labelledby="tab-year"
    tabindex="0"
    :style="activeTab === 'year' ? 'display:grid' : 'display:none'"
  )
    TabPanel(
      :datum="state.past_year"
      :time="state.time"
      :series="state.past_year_series"
      :axes="axes"
      :timeStep="13"
      timeFormat="d/m/Y"
      @showHelp="$emit('showHelp', $event)"
    )

  div#tab-panel-all(
    role="tabpanel"
    aria-labelledby="tab-all"
    tabindex="0"
    :style="activeTab === 'all' ? 'display:grid' : 'display:none'"
  )
    TabPanel(
      :datum="state.all_time"
      :time="state.time"
      :series="state.all_time_series"
      :axes="axes"
      :timeStep="1"
      timeFormat="Y"
      @showHelp="$emit('showHelp', $event)"
    )
</template>

<script setup lang="ts">
import type { GridState, AllAxes } from '~/types/grid'

const props = defineProps<{
  state: GridState
  axes: AllAxes
}>()

defineEmits<{
  showHelp: [help: string, label: string]
}>()

const tabs = ['day', 'week', 'year', 'all'] as const
type Tab = typeof tabs[number]

const activeTab = ref<Tab>('day')

function selectTab(tab: Tab) {
  activeTab.value = tab
}

function handleKeyDown(e: KeyboardEvent) {
  const idx = tabs.indexOf(activeTab.value)
  let newIdx = idx
  if (e.key === 'ArrowLeft')  newIdx = (idx + tabs.length - 1) % tabs.length
  if (e.key === 'ArrowRight') newIdx = (idx + 1) % tabs.length
  if (e.key === 'Home')       newIdx = 0
  if (e.key === 'End')        newIdx = tabs.length - 1
  if (newIdx !== idx) {
    e.preventDefault()
    selectTab(tabs[newIdx])
  }
}
</script>
