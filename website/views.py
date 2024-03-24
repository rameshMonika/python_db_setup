from flask import Blueprint,render_template,request, jsonify
from flask_login import login_required,current_user
from .controllers import get_flight_offers, get_flight_routes, read_airports_from_csv
import os

views=Blueprint('views',__name__)

@views.route('/')
@login_required
def home():
    return render_template("home.html",user=current_user)


@views.route('/get_route', methods=['GET'])
def get_route():
    print("get routes method started")
    origin = request.args.get('source').upper()
  
    destination = request.args.get('destination').upper()
   
    max_layovers = int(request.args.get('layover'))
  
    current_dir = os.path.dirname(__file__)

    filename = os.path.join(current_dir, 'data', 'airports_Asia.csv')  
    airports = read_airports_from_csv(filename)
    
    flight_routes = get_flight_routes(origin, destination, max_layovers, airports=airports)
    flight_offers = get_flight_offers(origin, destination)

    print("--------------------------------- views.py (flight route) ------------------------------------------")

    print(flight_routes)
    print("--------------------------------- views.py (flight offers) ------------------------------------------")

    print(flight_offers)
  
    
    return jsonify({"routes": flight_routes}, {"price": flight_offers})