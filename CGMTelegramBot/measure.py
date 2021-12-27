from . import settings
from datetime import datetime, timedelta


class Measure:

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


    def __init__(self, date: int, sgv: int, direction: str):
        self.date = date
        self.sgv = sgv
        self.direction = direction


    def direction_as_emoji(self) -> str:
        return Measure.direction_to_emoji_dict.get(self.direction, None)


    def triggers_alert(self) -> bool:
        return self.sgv >= settings.LIMIT_HIGH or self.sgv <= settings.LIMIT_LOW


    def local_time_str(self) -> str:
        date = datetime.fromtimestamp(self.date / 1000)
        date = date + timedelta(hours=-3)
        date_str = date.strftime("%d/%m/%Y - %H:%M")
        return date_str


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


    def __eq__(self, other) -> bool:
        if other is None:
            return False
        return self.date == other.date and self.sgv == other.sgv and self.direction == other.direction


    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
