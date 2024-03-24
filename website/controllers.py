import csv
import math
from amadeus import Client, ResponseError
from datetime import datetime

amadeus = Client(
    client_id='BxsFW8YgIcfqCGSiwk1GPvcJnttW266T',
    client_secret='WnFBmc33acG9bWHf'
)

def get_flight_offers(origin, destination):
    date = datetime.today().strftime('%Y-%m-%d')
    flight_offers = []
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=1,
            nonStop='true',
            currencyCode='SGD',
            max=5
        )

        for offer in response.data:
            flight_offers.append({
                "carrierCode": offer['itineraries'][0]['segments'][0]['carrierCode'],
                "priceSGD": offer['price']['total']
            })

    except ResponseError as error:
        print(error)

    return flight_offers

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def read_airports_from_csv(filename):
    airports = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            country = row[2]
            iata_code = row[3]
            lat = float(row[4])
            lon = float(row[5])
            airports[iata_code] = {'country': country, 'coords': (lat, lon)}
    return airports

def construct_graph(airports):
    graph = {}
    for origin_iata, origin_data in airports.items():
        origin_country = origin_data['country']
        connections = []
        for dest_iata, dest_data in airports.items():
            if origin_iata != dest_iata and origin_country != dest_data['country']:
                origin_coords = origin_data['coords']
                dest_coords = dest_data['coords']
                distance = calculate_distance(origin_coords[0], origin_coords[1], dest_coords[0], dest_coords[1])
                connections.append((dest_iata, distance))
        connections.sort(key=lambda x: x[1])
        graph[origin_iata] = [conn[0] for conn in connections]
    return graph

def dfs(graph, current, destination, max_layovers, path, routes, max_routes, airports):
    if len(path) - 1 > max_layovers + 1 or len(routes) >= max_routes:
        return
    if current == destination:
        routes.append(path)
        return
    for neighbor in graph.get(current, []):
        if neighbor not in path:
            dfs(graph, neighbor, destination, max_layovers, path + [neighbor], routes, max_routes, airports)

def get_flight_routes(origin, destination, max_layovers, airports):
    print("Accessing get flight routes ()")
    print(origin)
    print(destination)
    print(max_layovers)
    graph = construct_graph(airports)
    max_routes = 10
    routes = []
 

    if destination in graph.get(origin, []):
        routes.append([origin, destination])
        print(routes)

    if max_layovers == 0:
        direct_routes = []
        if routes:
            for route in routes:
                direct_routes.append(route)
            return direct_routes
        else:
            return []
    else:
        dfs(graph, origin, destination, max_layovers, [origin], routes, max_routes, airports)

        if routes:
            result_routes = []
            for route in routes:
                total_distance = 0
                for i in range(len(route) - 1):
                    origin_iata = route[i]
                    dest_iata = route[i + 1]
                    origin_coords = airports[origin_iata]['coords']
                    dest_coords = airports[dest_iata]['coords']
                    distance = calculate_distance(origin_coords[0], origin_coords[1], dest_coords[0], dest_coords[1])
                    total_distance += distance
                route.append(total_distance)
                result_routes.append(route)
         
            return result_routes
        else:
            return []
