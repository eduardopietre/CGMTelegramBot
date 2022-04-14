from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from CGMTelegramBot import settings


class DateEntry(ABC):

    @staticmethod
    @abstractmethod
    def from_json(data):
        pass
    
    def __init__(self, date: int):
        self.date = date

    def local_time_str(self) -> str:
        date = datetime.fromtimestamp(self.date / 1000)
        date = date + timedelta(hours=-3)
        date_str = date.strftime("%d/%m/%Y - %H:%M")
        return date_str

    def __lt__(self, other) -> bool:
        return self.date < other.date

    def __repr__(self) -> str:
        return self.__str__()

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class Measure(DateEntry):

    direction_to_emoji_dict = {
        "TripleUp": "↑↑↑",
        "DoubleUp": "↑↑",
        "SingleUp": "↑",
        "FortyFiveUp": "↗",
        "Flat": "→",
        "FortyFiveDown": "↘",
        "SingleDown": "↓",
        "DoubleDown": "↓↓",
        "TripleDown": "↓↓↓",
    }

    __slots__ = ("date", "sgv", "direction")

    @staticmethod
    def from_json(data):
        return Measure(data["date"], data["sgv"], data["direction"])


    def __init__(self, date: int, sgv: int, direction: str):
        super(Measure, self).__init__(date)
        self.sgv = sgv
        self.direction = direction


    def direction_as_emoji(self) -> str:
        return Measure.direction_to_emoji_dict.get(self.direction, None)


    def triggers_alert(self) -> bool:
        return self.sgv >= settings.LIMIT_HIGH or self.sgv <= settings.LIMIT_LOW


    def message(self) -> str:
        def get_keyword():
            if self.sgv >= settings.LIMIT_HIGH:
                return "Hiperglicemia"
            elif self.sgv <= settings.LIMIT_LOW:
                return "Hipoglicemia"
            else:
                return "Glicemia"

        keyword = get_keyword()
        arrow = self.direction_as_emoji()
        time_str = self.local_time_str()

        return f"{keyword}: {self.sgv} mg/dL {arrow}\n({time_str})"


    def __str__(self) -> str:
        return f"Measure({self.date}, {self.sgv}, {repr(self.direction)})"


    def __eq__(self, other) -> bool:
        if other is None:
            return False
        return self.date == other.date and self.sgv == other.sgv and self.direction == other.direction



class Treatment(DateEntry):

    __slots__ = ("date", "carbs", "insulin")

    @staticmethod
    def from_json(data):
        return Treatment(data["mills"], data["carbs"], data["insulin"])


    def __init__(self, date: int, carbs: int, insulin: str):
        super(Treatment, self).__init__(date)
        self.carbs = carbs
        self.insulin = insulin


    @property
    def is_carbs(self):
        return self.carbs is not None


    @property
    def is_insulin(self):
        return self.insulin is not None


    def __str__(self) -> str:
        return f"Treatment({self.date}, {self.carbs}, {self.insulin})"


    def __eq__(self, other) -> bool:
        if other is None:
            return False
        return self.date == other.date and self.carbs == other.carbs and self.insulin == other.insulin



def seconds_elapsed(measure_older: Measure, measure_newer: Measure) -> float:
    # Date is in milliseconds, divide by 1000 to convert.
    return (measure_newer.date - measure_older.date) / 1000


def apply_seconds_elapsed(measures: [Measure]) -> [float]:
    return [
        seconds_elapsed(measures[i], measures[i + 1])
        for i in range(len(measures) - 1)
    ]


def calculate_delta(measure_older: Measure, measure_newer: Measure) -> float:
    seconds_diff = seconds_elapsed(measure_older, measure_newer)
    minutes_diff = seconds_diff / 60
    sgv_diff = measure_newer.sgv - measure_older.sgv
    delta = sgv_diff / minutes_diff * 5
    delta = round(delta, 3)
    return delta


def apply_calculate_deltas(measures: [Measure]) -> [float]:
    return [
        calculate_delta(measures[i], measures[i + 1])
        for i in range(len(measures) - 1)
    ]
