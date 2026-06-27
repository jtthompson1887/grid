<template lang="pug">
section
  h2 About this site
  p
    | This site is an open source project by #[a(href="https://iamkate.com/") Kate Morley]. I've published #[a(href="https://github.com/KateMorley/grid") the code on GitHub] under the terms of the #[a(href="https://creativecommons.org/publicdomain/zero/1.0/legalcode") Creative Commons CC0 1.0 Universal Legal Code]. This means I've waived all copyright and related rights to the extent possible under law, with the intention of dedicating the code to the public domain. You can use and adapt it without attribution.
  p
    | If you'd like to thank me for the time I've spent working on this project, or help me cover the costs of hosting a site that received {{ formatVisits(state.yearly_visits) }} visits over the past year, #[a(href="https://ko-fi.com/katemorley") I do accept donations].
  div.visits-graph
    h3 Weekly visits
    GraphPanel(
      :series="state.past_year_series"
      :axes="axes.visits"
      graphKey="visits"
      prefix=""
      suffix=""
      :timeStep="13"
      timeFormat="d/m/Y"
      :decimalPlaces="0"
    )
  p
    | The data comes from the #[a(href="https://bmrs.elexon.co.uk/") Elexon Insights Solution], the #[a(href="https://www.neso.energy/data-portal") National Energy System Operator Data Portal], and the #[a(href="https://carbonintensity.org.uk/") Carbon Intensity API] (a project by the National Energy System Operator and the University Of Oxford Department Of Computer Science). #[a(href="https://www.elexon.co.uk/data/balancing-mechanism-reporting-agent/copyright-licence-bmrs-data/") Elexon's licence] requires the following statement: Contains BMRS data © Elexon Limited copyright and database right {{ currentYear }}.
</template>

<script setup lang="ts">
import type { GridState, AllAxes } from '~/types/grid'

const props = defineProps<{
  state: GridState
  axes: AllAxes
}>()

const { formatVisits } = useFormatters()
const currentYear = new Date().getFullYear()
</script>
