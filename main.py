from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flight_search import FlightSearch
from flight_data import FlightData
from flask_sqlalchemy import SQLAlchemy
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("APP_SECRET_KEY")
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///flight-db.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/subscribe")
def subscribe():
    return render_template("subscribe.html")


@app.route("/thankYou", methods=['POST'])
def success():
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(250), nullable=False)
        origin = db.Column(db.String(250), nullable=False)
        email = db.Column(db.String(250), nullable=False)

    name = request.form["username"]
    name1 = name.split(" ")
    if name1[0] == " ":
        name2 = name1[1].title()
    else:
        name2 = name1[0].title()
    origin_city = request.form["cityName"]
    email = request.form["email"]

    with app.app_context():
        db.create_all()

        new_user = User(name=f'{name2}', origin=f'{origin_city}', email=f'{email}')
        db.session.add(new_user)
        db.session.commit()

    return render_template("success.html")


@app.route('/search', methods=['POST'])
def search():
    return render_template("search.html")


@app.route('/bestFlights', methods=['POST'])
def get_flight():
    try:
        code_search = FlightSearch()
        flight_data = FlightData()

        origin = request.form["origin"]
        destination = request.form["destination"]
        departure_date = request.form["departure"]
        return_date = request.form["return"]
        flight_type = request.form["flight-type"]
        passengers = request.form["passengers"]

        depart_date = departure_date.split("-")
        depart_date_x = f"{depart_date[2]}/{depart_date[1]}/{depart_date[0]}"
        depart_date_y = f"{depart_date[2]}-{depart_date[1]}-{depart_date[0]}"
        depart_date_z = f"{depart_date[0]}-{depart_date[1]}-{depart_date[2]}"

        origin_code = code_search.get_destination_code(origin)
        destination_code = code_search.get_destination_code(destination)

        if flight_type == "oneway":
            ret_date_x = None

            data = flight_data.get_flight_deal(origin_code, destination_code, depart_date_x, ret_date_x,
                                               flight_type, int(passengers))

            origin_arrival = data['route'][0]['local_arrival'].split("T")[0].split("-")
            origin_arrivalx = f"{origin_arrival[2]}-{origin_arrival[1]}-{origin_arrival[0]}"

            depart_flight_num = f"{data['route'][0]['airline']}-{data['route'][0]['flight_no']}"

            origin_departure_time = data['route'][0]['local_departure'].split("T")[1].split(":")
            origin_departure_timex = f"{origin_departure_time[0]}:{origin_departure_time[1]}"

            origin_arrival_time = data['route'][0]['local_arrival'].split("T")[1].split(":")
            origin_arrival_timex = f"{origin_arrival_time[0]}:{origin_arrival_time[1]}"

            price = str(data['price'])

            if len(price) == 4:
                total_price = f"{price[:1]},{price[1:]}"
            elif len(price) == 5:
                total_price = f"{price[:2]},{price[2:]}"
            else:
                total_price = f"{price[:3]},{price[3:]}"

            url = f"https://www.kiwi.com/in/search/results/{origin}-india/{destination}-india/{depart_date_z}/no-return?sortBy=price&adults={passengers}"

            return render_template("flight-deal.html", flight_num=depart_flight_num, origin_code=origin_code,
                                   destination_code=destination_code, origin=origin.title(),
                                   destination=destination.title()
                                   , departure=depart_date_y, departure_time=origin_departure_timex,
                                   arrival=origin_arrivalx
                                   , arrival_time=origin_arrival_timex, price=total_price, kiwi_url=url)

        else:
            ret_date = return_date.split("-")
            ret_date_x = f"{ret_date[2]}/{ret_date[1]}/{ret_date[0]}"
            ret_date_y = f"{ret_date[2]}-{ret_date[1]}-{ret_date[0]}"
            ret_date_z = f"{ret_date[0]}-{ret_date[1]}-{ret_date[2]}"

            data = flight_data.get_flight_deal(origin_code, destination_code, depart_date_x, ret_date_x,
                                               flight_type, int(passengers))

            origin_arrival = data['route'][0]['local_arrival'].split("T")[0].split("-")
            origin_arrivalx = f"{origin_arrival[2]}-{origin_arrival[1]}-{origin_arrival[0]}"

            return_arrival = data['route'][1]['local_arrival'].split("T")[0].split("-")
            return_arrivalx = f"{return_arrival[2]}-{return_arrival[1]}-{return_arrival[0]}"

            depart_flight_num = f"{data['route'][0]['airline']}-{data['route'][0]['flight_no']}"
            return_flight_num = f"{data['route'][1]['airline']}-{data['route'][1]['flight_no']}"

            origin_departure_time = data['route'][0]['local_departure'].split("T")[1].split(":")
            origin_departure_timex = f"{origin_departure_time[0]}:{origin_departure_time[1]}"

            origin_arrival_time = data['route'][0]['local_arrival'].split("T")[1].split(":")
            origin_arrival_timex = f"{origin_arrival_time[0]}:{origin_arrival_time[1]}"

            return_departure_time = data['route'][1]['local_departure'].split("T")[1].split(":")
            return_departure_timex = f"{return_departure_time[0]}:{return_departure_time[1]}"

            return_arrival_time = data['route'][1]['local_arrival'].split("T")[1].split(":")
            return_arrival_timex = f"{return_arrival_time[0]}:{return_arrival_time[1]}"

            price = str(data['price'])

            if len(price) == 4:
                total_price = f"{price[:1]},{price[1:]}"
            elif len(price) == 5:
                total_price = f"{price[:2]},{price[2:]}"
            else:
                total_price = f"{price[:3]},{price[3:]}"

            url = f"https://www.kiwi.com/in/search/results/{origin}-india/{destination}-india/{depart_date_z}/{ret_date_z}?sortBy=price&adults={passengers}"

            return render_template("flight-deal-round.html", kiwi_url=url, depart_flight_num=depart_flight_num,
                                   return_flight_num=return_flight_num, origin_code=origin_code,
                                   destination_code=destination_code, origin=origin.title(),
                                   destination=destination.title()
                                   , origin_departure=depart_date_y, origin_departure_time=origin_departure_timex,
                                   dest_departure=ret_date_y, dest_departure_time=return_departure_timex,
                                   origin_arrival=origin_arrivalx, origin_arrival_time=origin_arrival_timex,
                                   dest_arrival=return_arrivalx, dest_arrival_time=return_arrival_timex,
                                   price=total_price)

    except:
        return render_template("denial.html")


if __name__ == '__main__':
    app.run(debug=True)
