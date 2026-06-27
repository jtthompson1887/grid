from dataclasses import dataclass, field
from .datum import Datum
from .record import Record


@dataclass
class State:
    time: int
    latest: Datum
    past_day: Datum
    past_week: Datum
    past_year: Datum
    all_time: Datum
    past_day_series: dict
    past_week_series: dict
    past_year_series: dict
    all_time_series: dict
    wind_record: Record
    wind_milestones: dict
    yearly_visits: int

    def to_dict(self) -> dict:
        def series_to_list(series: dict) -> list:
            return [
                {'time': t, 'datum': d.to_dict()}
                for t, d in series.items()
            ]

        milestones_list = [
            {'power': power, 'time': time}
            for power, time in self.wind_milestones.items()
        ]

        return {
            'time':             self.time,
            'latest':           self.latest.to_dict(),
            'past_day':         self.past_day.to_dict(),
            'past_week':        self.past_week.to_dict(),
            'past_year':        self.past_year.to_dict(),
            'all_time':         self.all_time.to_dict(),
            'past_day_series':  series_to_list(self.past_day_series),
            'past_week_series': series_to_list(self.past_week_series),
            'past_year_series': series_to_list(self.past_year_series),
            'all_time_series':  series_to_list(self.all_time_series),
            'wind_record':      {'time': self.wind_record.time, 'power': self.wind_record.power},
            'wind_milestones':  milestones_list,
            'yearly_visits':    self.yearly_visits,
        }
