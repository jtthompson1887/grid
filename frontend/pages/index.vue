<template lang="pug">
div
  AppHeader
  main(v-if="state")
    h1 National Grid: Live
    p The National Grid is the electric power transmission network for Great Britain
    div#status.columns
      section
        StatusPanel(:datum="state.latest" :time="state.time" :showHelp="true" @showHelp="handleShowHelp")
      section
        EquationPanel(:datum="state.latest" :showHelp="true" @showHelp="handleShowHelp")
    LatestPanel(:datum="state.latest" @showHelp="handleShowHelp")
    TabsSection(:state="state" :axes="axes" @showHelp="handleShowHelp")
    div.columns
      TransitionSection(:state="state")
      AboutSection(:state="state" :axes="axes")
  main(v-else)
    h1 National Grid: Live
    p Loading…
  AppFooter
  HelpDialog(ref="helpDialog")
</template>

<script setup lang="ts">
import type { GridState, AllAxes } from '~/types/grid'

useHead({
  title: 'National Grid: Live',
  meta: [
    { name: 'description', content: 'Shows the live status of Great Britain\'s electric power transmission network' },
    { name: 'viewport', content: 'width=device-width,initial-scale=1' },
    { name: 'fediverse:creator', content: '@katemorley@hachyderm.io' },
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: 'National Grid: Live' },
    { name: 'twitter:description', content: 'Shows the live status of Great Britain\'s electric power transmission network' },
    { name: 'twitter:image', content: 'https://grid.iamkate.com/banner.png' },
    { name: 'twitter:site', content: '@KateRoseMorley' },
    { property: 'og:url', content: 'https://grid.iamkate.com/' },
    { property: 'og:type', content: 'website' },
    { property: 'og:title', content: 'National Grid: Live' },
    { property: 'og:image', content: 'https://grid.iamkate.com/banner.png' },
  ],
  link: [
    { rel: 'canonical', href: 'https://grid.iamkate.com/' },
    { rel: 'preload', href: '/proza-regular.woff2', as: 'font', type: 'font/woff2', crossorigin: '' },
    { rel: 'preload', href: '/proza-light.woff2', as: 'font', type: 'font/woff2', crossorigin: '' },
    { rel: 'icon', href: '/favicon.png', type: 'image/png' },
    { rel: 'icon', href: '/api/favicon.svg', type: 'image/svg+xml' },
  ]
})

const { data, refresh } = useGridState()

const state = computed<GridState | null>(() => data.value ?? null)

const axes = computed<AllAxes>(() => {
  if (!state.value) {
    return {
      price: { minimum: 0, maximum: 100, step: 10 },
      emissions: { minimum: 0, maximum: 500, step: 100 },
      generation: { minimum: 0, maximum: 50, step: 10 },
      transfers: { minimum: -5, maximum: 5, step: 1 },
      demand: { minimum: 0, maximum: 50, step: 10 },
      visits: { minimum: 0, maximum: 100000, step: 100000 },
    }
  }
  return useGraphAxes(
    state.value.past_day_series,
    state.value.past_week_series,
    state.value.past_year_series,
    state.value.all_time_series,
  )
})

const helpDialog = ref<{ open: (help: string, label: string) => void } | null>(null)

function handleShowHelp(help: string, label: string) {
  helpDialog.value?.open(help, label)
}

onMounted(() => {
  const { start, stop } = useLiveUpdates(async () => {
    await refresh()
  })
  start()
  onUnmounted(stop)
})
</script>
