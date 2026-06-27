import type { SeriesEntry, AxesData, AllAxes } from '~/types/grid'

const VISITS_STEP = 100000

type GraphKey = 'price' | 'emissions' | 'generation' | 'transfers' | 'demand' | 'visits'

function getMapValues(entry: SeriesEntry, graphKey: GraphKey): number[] {
  const d = entry.datum
  switch (graphKey) {
    case 'price':        return Object.values(d.price)
    case 'emissions':    return Object.values(d.emissions)
    case 'generation':   return Object.values(d.generation)
    case 'transfers':    return Object.values(d.transfers)
    case 'demand':       return Object.values(d.demand)
    case 'visits':       return Object.values(d.visits)
  }
}

function computeAxis(
  allSeries: SeriesEntry[][],
  graphKey: GraphKey,
  step?: number
): AxesData {
  const minimums: number[] = [0]
  const maximums: number[] = []

  for (const series of allSeries) {
    for (const entry of series) {
      const vals = getMapValues(entry, graphKey)
      minimums.push(Math.min(...vals))
      maximums.push(Math.max(...vals))
    }
  }

  const minimum = Math.min(...minimums)
  const maximum = Math.max(...maximums, 0)
  const range = maximum - minimum

  if (step === undefined) {
    if (range > 2000)      step = 500
    else if (range > 1000) step = 200
    else if (range > 500)  step = 100
    else if (range > 200)  step = 50
    else if (range > 100)  step = 20
    else if (range > 50)   step = 10
    else if (range > 20)   step = 5
    else if (range > 10)   step = 2
    else                   step = 1
  }

  return {
    minimum: step * Math.floor(minimum / step),
    maximum: step * Math.ceil(maximum / step),
    step,
  }
}

export function useGraphAxes(
  pastDaySeries: SeriesEntry[],
  pastWeekSeries: SeriesEntry[],
  pastYearSeries: SeriesEntry[],
  allTimeSeries: SeriesEntry[]
): AllAxes {
  const allSeries = [pastDaySeries, pastWeekSeries, pastYearSeries, allTimeSeries]

  const price      = computeAxis(allSeries, 'price')
  const emissions  = computeAxis(allSeries, 'emissions')
  const generation = computeAxis(allSeries, 'generation')
  const transfers  = computeAxis(allSeries, 'transfers')
  const demand     = computeAxis(allSeries, 'demand')
  const visits     = computeAxis([pastYearSeries], 'visits', VISITS_STEP)

  return { price, emissions, generation, transfers, demand, visits }
}
