from typing import Optional
import pymongo
from pymongo import MongoClient
from . import settings
from .measure import Measure


class Database:

    def __init__(self):
        self.client = MongoClient(settings.MONGO_HOST)
        self.database = self.client[settings.MONGO_DB_NAME]
        self.collection = self.database[settings.MONGO_COLLECTION_NAME]


    def latest_entry(self) -> Optional[dict]:
        return self.collection.find_one(sort=[("date", pymongo.DESCENDING)])


    def latest_measure(self) -> Measure:
        latest = self.latest_entry()
        date = latest["date"]
        sgv = latest["sgv"]
        direction = latest["direction"]

        return Measure(date, sgv, direction)
