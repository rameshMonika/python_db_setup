from flask import Blueprint,render_template,request, jsonify
from flask_login import login_required,current_user
from .controllers import read_airports_from_csv,amadeus,construct_graph,print_flight_routes,dfs
import os

views=Blueprint('views',__name__)

@views.route('/')
@login_required
def home():
    return render_template("home.html",user=current_user)


@views.route('/get_route', methods=['POST'])
def search_flights():
    data = request.get_json()
    origin = data.get('origin')
    destination = data.get('destination')
    departure_date = data.get('departure_date')
    direct_flight = data.get('direct_flight')

    # Read airports data from CSV file
    current_dir = os.path.dirname(__file__)

    filename = os.path.join(current_dir, 'data', 'airports_Asia.csv')  
    airports = read_airports_from_csv(filename)

    # Construct the graph based on airport distances
    graph = construct_graph(airports)

    # Retrieve flight data for the given origin-destination pair
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode=origin,
        destinationLocationCode=destination,
        departureDate=departure_date,
        adults=1,
        currencyCode='SGD',
        nonStop='false',
        max=50
    )

    response_data = response.data

    if response_data:
        direct_route = [origin, destination] if destination in graph.get(origin, []) else None

        if direct_flight:
            direct_data, _ = print_flight_routes(graph, direct_route, [], response_data, airports, origin, destination)
            return jsonify({'direct_flight_data': direct_data})
        else:
            routes = dfs(graph, origin, destination, 2, [origin], response_data)
            
            _, indirect_data = print_flight_routes(graph, [], routes, response_data, airports, origin, destination)
            return jsonify({'indirect_flight_data': indirect_data})
    else:
        return jsonify({'error': 'No flight data available.'})


# @views.route('/get_route', methods=['GET'])
# def get_route():
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