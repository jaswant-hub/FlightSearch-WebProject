import requests
# from dotenv import load_dotenv
# import os

# load_dotenv()

TEQUILA_ENDPOINT = "https://tequila-api.kiwi.com"
TEQUILA_API = "Yo6xXSSwdsdgoxra8RtaDzaGCTHohNbt"
SEARCH_LOCATION_EP = f"{TEQUILA_ENDPOINT}/locations/query"


class FlightSearch:

    def get_destination_code(self, city_name):
        header = {
            "apikey": TEQUILA_API
        }

        search_params = {
            "term": city_name
        }

        response = requests.get(url=SEARCH_LOCATION_EP, params=search_params, headers=header)
        data = response.json()
        return data['locations'][0]['code']
