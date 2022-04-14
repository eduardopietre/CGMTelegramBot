from .data import Measure, Treatment, apply_seconds_elapsed, apply_calculate_deltas

from typing import Optional


class AnalyzerData:

    def __init__(self, measures: [Measure], treatments: [Treatment]):
        self.measures = sorted(measures)
        self.measures_seconds_elapsed = apply_seconds_elapsed(self.measures)
        self.measures_deltas = apply_calculate_deltas(self.measures)
        self.treatments = sorted(treatments)


    @property
    def insulin(self):
        return [t for t in self.treatments if t.is_insulin]


    @property
    def carbs(self):
        return [t for t in self.treatments if t.is_carbs]


    @property
    def newest_insulin(self) -> Optional[Treatment]:
        insulin = self.insulin
        return insulin[-1] if len(insulin) > 0 else None


    @property
    def newest_carb(self) -> Optional[Treatment]:
        carbs = self.carbs
        return carbs[-1] if len(carbs) > 0 else None


    def latest(self, n):
        return AnalyzerData(self.measures[-n:], self.treatments[-n:])
