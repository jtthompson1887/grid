export interface MapData {
  [key: string]: number
}

export interface DatumData {
  price: MapData
  emissions: MapData
  generation: MapData
  types: MapData
  interconnectors: MapData
  storage: MapData
  transfers: MapData
  demand: MapData
  visits: MapData
  total: number
}

export interface RecordData {
  time: number
  power: number
}

export interface SeriesEntry {
  time: number
  datum: DatumData
}

export interface WindMilestone {
  power: number
  time: number
}

export interface GridState {
  time: number
  latest: DatumData
  past_day: DatumData
  past_week: DatumData
  past_year: DatumData
  all_time: DatumData
  past_day_series: SeriesEntry[]
  past_week_series: SeriesEntry[]
  past_year_series: SeriesEntry[]
  all_time_series: SeriesEntry[]
  wind_record: RecordData
  wind_milestones: WindMilestone[]
  yearly_visits: number
}

export interface AxesData {
  minimum: number
  maximum: number
  step: number
}

export interface AllAxes {
  price: AxesData
  emissions: AxesData
  generation: AxesData
  transfers: AxesData
  demand: AxesData
  visits: AxesData
}
