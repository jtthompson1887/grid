<template lang="pug">
div#latest
  section#generation
    h2 Generation
    div.pie-chart-container
      PieChart(:datum="datum")
    div Note: percentages are relative to demand, so will exceed 100% if power is being exported

  section#fossils
    h2 {{ formatPercentage(datum.types.fossils / demand) }}% fossil fuels
    SourcesTable(
      :mapData="datum.generation"
      :keys="fossilKeys"
      :demand="demand"
      @showHelp="$emit('showHelp', $event)"
    )

  section#renewables
    h2 {{ formatPercentage(datum.types.renewables / demand) }}% renewables
    SourcesTable(
      :mapData="datum.generation"
      :keys="renewableKeys"
      :demand="demand"
      @showHelp="$emit('showHelp', $event)"
    )

  section#others
    h2 {{ formatPercentage(datum.types.others / demand) }}% other sources
    SourcesTable(
      :mapData="datum.generation"
      :keys="otherKeys"
      :demand="demand"
      @showHelp="$emit('showHelp', $event)"
    )

  section#transfers
    h2 {{ formatPercentage(interconnectorTotal / demand) }}% interconnectors
    SourcesTable(
      :mapData="datum.interconnectors"
      :keys="interconnectorKeys"
      :demand="demand"
      :isTransfers="true"
      @showHelp="$emit('showHelp', $event)"
    )

  section#storage
    h2 {{ formatPercentage(storageTotal / demand) }}% storage
    SourcesTable(
      :mapData="datum.storage"
      :keys="storageKeys"
      :demand="demand"
      :isTransfers="true"
      @showHelp="$emit('showHelp', $event)"
    )
</template>

<script setup lang="ts">
import type { DatumData } from '~/types/grid'

const props = defineProps<{
  datum: DatumData
}>()

defineEmits<{
  showHelp: [help: string, label: string]
}>()

const { formatPercentage } = useFormatters()

const demand = computed(() => props.datum.total || 1)
const interconnectorTotal = computed(() => Object.values(props.datum.interconnectors).reduce((a, b) => a + b, 0))
const storageTotal = computed(() => Object.values(props.datum.storage).reduce((a, b) => a + b, 0))

const fossilKeys = [
  {
    key: 'gas', label: 'Gas',
    help: "<p>Gas-fired power stations burn natural gas to drive a turbine. Most gas-fired power stations use the excess heat from burning the gas to produce steam to drive a second turbine. Burning natural gas causes carbon dioxide and other pollutants to be emitted, worsening the climate crisis and damaging human health.</p><p>In 2001 the European Union issued the Large Combustion Plant Directive, obliging power stations to limit their emissions or close by 2015. Most coal-fired power stations in Great Britain closed in response, with gas-fired power stations taking over as the largest source of Great Britain's power.</p>"
  }
]

const renewableKeys = [
  {
    key: 'solar', label: 'Solar',
    help: "<p>Solar panels generate power from the photovoltaic effect, where light falling on a material produces an electric current.</p><p>Despite Great Britain's northerly latitude and frequently cloudy conditions, solar panels are still able to generate a useful amount of power. Rooftop solar panels on residential buildings have become increasingly popular as the price of solar panels has fallen.</p><p>Solar panels are connected to the local distribution network rather than the national transmission network, so their reported power generation is an estimate from National Grid ESO, based on weather conditions and observed transmission network demand.</p>"
  },
  {
    key: 'wind', label: 'Wind',
    help: "<p>Wind turbines generate power from the movement of air. Turbines can be located on land (onshore) or at sea (offshore). Offshore wind turbines benefit from higher and more consistent wind speeds.</p><p>Great Britain's exposed position in the north-east Atlantic makes it one of the best locations in the world for wind power generation, and the shallow waters of the North Sea host several of the world's largest offshore wind farms.</p><p>Onshore wind turbines in England and Wales (and some in Scotland) are connected to the local distribution network rather than the national transmission network, so their reported power generation is an estimate from National Grid ESO, based on weather conditions and observed transmission network demand. Offshore wind turbines (and many onshore wind turbines in Scotland) are connected to the transmission network and their power generation is measured directly.</p>"
  },
  {
    key: 'hydro', label: 'Hydroelectric',
    help: "<p>Hydroelectric turbines generate power from the movement of water. Large hydroelectric systems use a reservoir held back by a dam to provide water at a controlled rate. Smaller hydroelectric systems located on rivers rely on the variable flow of the river.</p><p>Large hydroelectric systems make use of mountainous topography to contain their reservoirs, so most of Great Britain's hydroelectric systems are located in Scotland, with a smaller number in Wales and a few in England.</p>"
  }
]

const otherKeys = [
  {
    key: 'nuclear', label: 'Nuclear',
    help: "<p>Nuclear power stations use the heat produced from the radioactive decay of uranium to produce steam to drive a turbine. The world's first commercial nuclear power station, Calder Hall in Cumbria, started producing power on 27th August 1956.</p><p>The risk of accidents releasing radioactive material makes nuclear power controversial. Great Britain's worst nuclear accident happened on 10th October 1957 when a reactor at Windscale (now known as Sellafield) in Cumbria caught fire. The accident is believed to have caused around 240 cases of cancer, about half of which were fatal. Decommissioning of the site is ongoing.</p><p>Great Britain's nuclear programme has produced around 150,000 cubic metres of radioactive waste to date, most of which is stored in temporary facilities at Sellafield in Cumbria and Dounreay in Scotland. There are plans for a permanent disposal site deep underground, but it has been difficult to find a location suitable for storing radioactive waste for 100,000 years.</p>"
  },
  {
    key: 'biomass', label: 'Biomass',
    help: "<p>Biomass power stations burn plant material to produce steam to drive a turbine. Great Britain's largest power station, Drax, is a former coal-fired power station converted to burn wood pellets.</p><p>Biomass power stations qualify for renewable energy subsidies (over £6bn so far in the case of Drax) because newly planted trees can absorb the carbon dioxide produced by burning wood from mature trees. However, this process can take decades, during which time the effects on atmospheric carbon dioxide levels are worse than those from burning fossil fuels.</p><p>Furthermore, Drax imports most of its wood pellets, and <a href='https://www.bbc.co.uk/news/science-environment-63089348'>a BBC investigation</a> found that Drax was clearfelling irreplaceable old-growth forests in Canada.</p>"
  }
]

const interconnectorKeys = [
  { key: 'belgium', label: 'Belgium', help: "<p>There is one link between Great Britain and Belgium:</p><p>Nemo Link is a 1<abbr>GW</abbr> link between Richborough in England and Zeebrugge in Belgium. It entered service in 2019.</p>" },
  { key: 'denmark', label: 'Denmark', help: "<p>There is one link between Great Britain and Denmark:</p><p>Viking Link is a 1.4<abbr>GW</abbr> link between Bicker Fen in England and Revsing in Denmark. It entered service in 2023.</p>" },
  { key: 'france', label: 'France', help: "<p>There are three links between Great Britain and France:</p><p>IFA (Interconnexion France–Angleterre) is a 2<abbr>GW</abbr> link between Sellindge in England and Bonningues-lès-Calais in France. It entered service in 1986.</p><p>IFA-2 (Interconnexion France–Angleterre 2) is a 1<abbr>GW</abbr> link between Warsash in England and Tourbe in France. It entered service in 2021.</p><p>ElecLink is a 1<abbr>GW</abbr> link between Folkestone in England and Peuplingues in France, running through the Channel Tunnel. It entered service in 2022.</p>" },
  { key: 'ireland', label: 'Ireland', help: "<p>Since 2007 the Republic of Ireland and Northern Ireland have formed a single electricity market. There are three links between Great Britain and the island of Ireland:</p><p>Moyle is a 0.5<abbr>GW</abbr> link between Auchencrosh in Scotland and Ballycronan More in Northern Ireland. It entered service in 2001.</p><p>EWIC (the East–West Interconnector) is a 0.5<abbr>GW</abbr> link between Shotton in Wales and Rush North Beach in the Republic of Ireland. It entered service in 2012.</p><p>Greenlink is a 0.5<abbr>GW</abbr> link between Freshwater West in Wales and Baginbun Beach in the Republic of Ireland. It entered service in 2024.</p>" },
  { key: 'netherlands', label: 'Netherlands', help: "<p>There is one link between Great Britain and the Netherlands:</p><p>BritNed is a 1<abbr>GW</abbr> link between the Isle of Grain in England and Maasvlakte in the Netherlands. It entered service in 2011.</p>" },
  { key: 'norway', label: 'Norway', help: "<p>There is one link between Great Britain and Norway:</p><p>NSL (the North Sea Link) is a 1.4<abbr>GW</abbr> link between Blyth in England and Kvilldal in Norway. It entered service in 2021.</p>" }
]

const storageKeys = [
  { key: 'pumped', label: 'Pumped storage', help: "<p>Pumped storage systems use electricity when it is comparatively cheap to pump water from a lower reservoir into a higher reservoir. When electricity is comparatively expensive the water is released, driving turbines to produce power.</p><p>Negative values mean water is being pumped, while positive values mean power is being generated.</p>" },
  { key: 'battery', label: 'Battery storage', help: "<p>Battery storage systems use electricity when it is comparatively cheap to charge a group of batteries. When electricity is comparatively expensive the batteries are discharged.</p><p>Several battery storage systems are in operation in Great Britain, but full reporting is not yet available: reports include discharging but not charging. As this would lead to double counting, with power being reported both when originally generated and when discharged from battery storage systems, battery storage data is not yet shown on this site.</p>", isDash: true }
]
</script>
