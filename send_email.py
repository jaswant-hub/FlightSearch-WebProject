from flight_search import FlightSearch
from flight_data import FlightData
from notification_manager import NotificationManager
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///flight-db.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Price(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(250), nullable=False)
    IATA = db.Column(db.String(250), nullable=False)
    pricing = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'({self.id}, {self.city}, {self.IATA}, {self.pricing})'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    origin = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'({self.name}, {self.origin}, {self.email})'


news_search = FlightSearch()
flight_data_news = FlightData()
flight_notification = NotificationManager()


with app.app_context():
    all_users = db.session.query(User).all()
    for user in all_users:
        all_prices = db.session.query(Price).all()

        for result in all_prices:
            destination_code = news_search.get_destination_code(result.city)
            origin_code = news_search.get_destination_code(user.origin)
            if result.city is None:
                code_to_update = Price.query.get(result.id)
                code_to_update.IATA = f"{destination_code}"

            data = flight_data_news.get_news_flights(origin_code, destination_code)

            if data is None:
                continue

            price = data['price']
            index = 1

            if price is not None and price < result.pricing:
                local_depart = data['route'][0]['local_departure'].split("T")[0]
                destination_depart = data['route'][index]['local_departure'].split("T")[0]
                stop_over_depart = data['route'][0]['cityTo']

                msg = f"Low Price Alert! Only Rs.{price} to fly from {data['cityFrom']}-{data['route'][0]['flyFrom']} to {data['cityTo']}-{data['route'][0]['flyTo']} from {local_depart} to {destination_depart}.\n"
                link = f"https://www.kiwi.com/in/search/results/bengaluru-india/patna-india/2022-12-01_2023-06-31/7" \
                       f"-28?sortBy=price "
                if flight_data_news.stop_overs > 0:
                    index = 2
                    msg += f"\nFlight has {flight_data_news.stop_overs} stop over via {stop_over_depart}"

                flight_notification.send_emails(msg, link, user.name, user.email)
