from typing import Optional

from .connection import Connection
from .analyzer_data import AnalyzerData, Measure
from .rules import apply_rules


class Analyzer:


    def __init__(self, url, secret):
        self.connection = Connection(url, secret)
        self.data = None


    def get_new_data(self):
        try:
            measures = self.connection.get_measures(16)
            treatments = self.connection.get_treatments(16)

        except Exception as e:
            print(f"Analyzer get_new_data exception: {e}")
            return False

        self.data = AnalyzerData(measures, treatments)
        return True


    def latest_measure(self) -> Optional[Measure]:
        if self.data and len(self.data.measures) > 0:
            return self.data.measures[-1]
        return None


    def rules_message(self) -> str:
        return apply_rules(self.data)
