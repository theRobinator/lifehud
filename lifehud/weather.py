from datetime import datetime, timedelta
from forecastiopy import ForecastIO, FIOHourly


UPDATE_INTERVAL = timedelta(minutes=15)


class Weather(object):
    """ The Weather class wraps the Dark Sky API to return the upcoming forecast. """
    last_updated = None
    data = None
    position_api = None
    api_key = None
    location = None

    @staticmethod
    def initialize(config):
        Weather.api_key = config['api_key']
        Weather.location = config['location']

    @staticmethod
    def get_forecast():
        if Weather.last_updated is not None and datetime.now() - UPDATE_INTERVAL < Weather.last_updated:
            return Weather.data

        Weather.position_api = ForecastIO.ForecastIO(Weather.api_key, latitude=Weather.location[0], longitude=Weather.location[1])

        Weather.data = FIOHourly.FIOHourly(Weather.position_api)
        Weather.last_updated = datetime.now()
        return Weather.data
