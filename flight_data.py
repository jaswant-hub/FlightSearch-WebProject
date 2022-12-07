import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

flight_data_endpoint = "https://api.tequila.kiwi.com/v2/search"
TEQUILA_API = os.getenv("TEQUILA_API")


class FlightData:
    def __init__(self):
        self.stop_overs = 0

    def get_flight_deal(self, origin_city_code, destination_city_code, depart_date, return_date, flight_type, adults):

        headers = {
            "apikey": TEQUILA_API
        }
        data_params = {
            "fly_from": origin_city_code,
            "fly_to": destination_city_code,
            "date_from": depart_date,
            "date_to": depart_date,
            "return_from": return_date,
            "return_to": return_date,
            "flight_type": flight_type,
            "one_for_city": 1,
            "adults": adults,
            "curr": "INR",
            "max_stopovers": self.stop_overs
        }

        response = requests.get(url=flight_data_endpoint, params=data_params, headers=headers)

        try:
            flight_data = response.json()["data"][0]
        except IndexError:
            data_params["max_stopovers"] = 1
            response = requests.get(url=flight_data_endpoint, params=data_params, headers=headers)
            try:
                data = response.json()["data"][0]
            except IndexError:
                return None
            else:
                self.stop_overs = 1
                return data
        else:
            return flight_data

    def get_news_flights(self, origin_city_code, destination_city_code):
        now = datetime.now()
        tomm = now + timedelta(1)
        tomm_date = tomm.strftime("%d/%m/%Y")
        six_month = tomm + timedelta(60*3)
        six_month_date = six_month.strftime("%d/%m/%Y")

        headers = {
            "apikey": TEQUILA_API
        }
        data_params = {
            "fly_from": origin_city_code,
            "fly_to": destination_city_code,
            "date_from": tomm_date,
            "date_to": six_month_date,
            "nights_in_dst_from": 7,
            "nights_in_dst_to": 28,
            "flight_type": "round",
            "one_for_city": 1,
            "curr": "INR",
            "max_stopovers": self.stop_overs
        }

        response = requests.get(url=flight_data_endpoint, params=data_params, headers=headers)

        try:
            flight_data = response.json()["data"][0]
        except IndexError:
            data_params["max_stopovers"] = 1
            response = requests.get(url=flight_data_endpoint, params=data_params, headers=headers)
            try:
                data = response.json()["data"][0]
            except IndexError:
                return None
            else:
                self.stop_overs = 1
                return data
        else:
            return flight_data
