import json
import requests
from .data import Measure, Treatment



class Connection:

    def __init__(self, url, secret):

        if url[-1] == "/" or url[-1] == "\\":
            url = url[:-1]

        self.url = url
        self.secret = secret


    def __perform_get(self, extra_url):
        url = self.url + extra_url

        headers = {
            "api-secret": self.secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        req = requests.get(url, headers=headers)
        data = json.loads(req.content)
        return data


    def get_measures(self, amount: int) -> [Measure]:
        data = self.__perform_get(f"/api/v1/entries?count={amount}")
        measures = [Measure.from_json(d) for d in data]
        return measures


    def get_treatments(self, amount: int) -> [Measure]:
        data = self.__perform_get(f"/api/v1/treatments?count={amount}")
        treatments = [Treatment.from_json(d) for d in data]
        return treatments


    def latest_measure(self) -> Measure:
        return self.get_measures(1)[0]

