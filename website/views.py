from flask import Blueprint,render_template,request, jsonify,flash,redirect,url_for
from flask_login import login_required,current_user
from .controllers import read_airports_from_csv,amadeus,construct_graph,print_flight_routes,dfs,find_optimal_route,print_optimal_route,display_top_usable_vouchers
import os
from .trie import Trie
import csv

views=Blueprint('views',__name__)

trie=Trie()




project_dir = os.path.dirname(__file__)

csv_file_path = os.path.join(project_dir, 'data', 'airports_Asia.csv')  

with open(csv_file_path, 'r',encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header row
    for row in reader:
        trie.insert(row[3])  # Inserting Airport Code


@views.route('/')
@login_required
def home():
    return render_template("home.html",user=current_user)


# @views.route('/bookFlights', methods=['GET', 'POST'])
# def input_form():
#     if request.method == 'POST':
#         ticket_price = request.form.get('ticket_price')
        
     
#         print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    
#         print(ticket_price)
#         print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

#     return render_template('bookFlights.html',ticket_price=ticket_price)

@views.route('/vouchers', methods=['GET', 'POST'])
def input_form_Result():
     if request.method == 'POST':
         passengers = int(request.form['passengers'])
        
         ticket_price = float(request.form['ticket_price'])
         # Redirect to the route displaying top usable vouchers
         top_usable_vouchers = display_top_usable_vouchers(passengers, ticket_price)
         return render_template('vouchers.html', passengers=passengers, ticket_price=ticket_price, vouchers=top_usable_vouchers)
     return render_template('vouchers.html')

@views.route('/display_vouchers', methods=['POST'])
def display_vouchers():
    if request.method == 'POST':
        passengers = int(request.form['passengers'])
        ticket_price = float(request.form['ticket_price'])
        top_usable_vouchers = display_top_usable_vouchers(passengers, ticket_price)
        return render_template('vouchers.html', passengers=passengers, ticket_price=ticket_price, vouchers=top_usable_vouchers)

    return jsonify({'error': 'Invalid request.'})


@views.route('/bookFlights', methods=['GET', 'POST'])
def input_form():
    if request.method == 'POST':
        # Check if 'ticket_price' exists in the form data
        source = request.form.get('source_airport')
        destination = request.form.get('destination_airport')
        departure_date = request.form.get('departure_date')
        airline = request.form.get('airline')
        route=request.form.get('route')
        ticket_price = request.form.get('ticket_price')
       
        if ticket_price:
            # Route to handle data submission from home.html
            print("Data received from home.html:", ticket_price)
            print("Data received from home.html:", source)
            print("Data received from home.html:", destination)
            print("Data received from home.html:", departure_date)
            print("Data received from home.html:", airline)
            print("Data received from home.html:", route)
            return render_template('bookFlights.html',  ticket_price=ticket_price,source=source,destination=destination,departure_date=departure_date,airline=airline,route=route)
          
          
        # else:
        #     # Route to handle data submission from bookFlights.html
        #     passengers = int(request.form['passengers'])
        #     ticket_price = float(request.form['ticket_price'])
        #     top_usable_vouchers = display_top_usable_vouchers(passengers, ticket_price)
        #     return render_template('bookFlights.html', passengers=passengers, ticket_price=ticket_price, vouchers=top_usable_vouchers)

    return render_template('bookFlights.html')


# @views.route('/display_vouchers')
# def display_vouchers():
#     passengers = int(request.args.get('passengers'))
#     ticket_price = float(request.args.get('ticket_price'))
#     top_usable_vouchers = display_top_usable_vouchers(passengers, ticket_price)
#     print(passengers)
#     print(ticket_price)
#     print(top_usable_vouchers)
#     return render_template('vouchers.html', vouchers=top_usable_vouchers)



@views.route('/suggest', methods=['GET'])
def suggest():
    prefix = request.args.get('prefix', '')
    suggestions = trie.get_suggestions(prefix)
    return jsonify(suggestions)


@views.route('/get_route', methods=['POST'])
def search_flights():
    data = request.get_json()
    origin = data.get('origin')
    destination = data.get('destination')
    departure_date = data.get('departure_date')
    direct_flight = data.get('direct_flight')
    sortOrder = data.get('sortOrder')

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
            direct_data, _ = print_flight_routes(graph, direct_route, [], response_data, airports, origin, destination,sort_order=sortOrder)
           # _, indirect_data=()
            optimal_route = find_optimal_route(graph, direct_route, [], response_data, airports, origin, destination)
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            optimal_route_data=print_optimal_route(optimal_route, response_data, graph, airports)
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            return jsonify({'direct_flight_data': direct_data},{'optimal_route_data':optimal_route_data})

        else:
            routes = dfs(graph, origin, destination, 2, [origin], response_data)
            
            _, indirect_data = print_flight_routes(graph, [], routes, response_data, airports, origin, destination,sort_order=sortOrder)
            optimal_route = find_optimal_route(graph, direct_route, [], response_data, airports, origin, destination)
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            optimal_route_data=print_optimal_route(optimal_route, response_data, graph, airports)
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
           # direct_data, _=()
            return jsonify({'indirect_flight_data': indirect_data},{'optimal_route_data':optimal_route_data})

    else:
        return jsonify({'error': 'No flight data available.'})

