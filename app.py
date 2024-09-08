# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from datetime import datetime, timedelta
import csv

app = Flask(__name__)
CORS(app)

# Load data from CSV file
def load_city_data(file_path='indian_cities.csv'):
    cities = {}
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            city = row['city']
            cities[city] = {
                'attractions': [row['attraction1'], row['attraction2'], row['attraction3'], row['attraction4']],
                'hotels': {
                    'budget': row['hotel1'],
                    'mid': row['hotel2'],
                    'luxury': row['hotel3']
                },
                'restaurants': [row['restaurant1'], row['restaurant2'], row['restaurant3']],
                'transport': [row['transport1'], row['transport2'], row['transport3']],
                'costs': {
                    'hotel': {
                        'budget': int(row['hotel_cost_budget']),
                        'mid': int(row['hotel_cost_mid']),
                        'luxury': int(row['hotel_cost_luxury'])
                    },
                    'food': {
                        'budget': int(row['food_cost_budget']),
                        'mid': int(row['food_cost_mid']),
                        'luxury': int(row['food_cost_luxury'])
                    },
                    'transport': {
                        'budget': int(row['transport_cost_budget']),
                        'mid': int(row['transport_cost_mid']),
                        'luxury': int(row['transport_cost_luxury'])
                    }
                }
            }
    return cities

indian_cities = load_city_data()

def generate_itinerary(source, destination, num_days, cost_option):
    itinerary = []
    current_date = datetime.now()

    for day in range(1, num_days + 1):
        daily_plan = {
            "day": day,
            "date": current_date.strftime("%Y-%m-%d"),
            "activities": random.sample(indian_cities[destination]["attractions"], 2),
            "hotel": indian_cities[destination]["hotels"][cost_option],
            "restaurant": random.choice(indian_cities[destination]["restaurants"]),
            "transport": random.choice(indian_cities[destination]["transport"])
        }
        itinerary.append(daily_plan)
        current_date += timedelta(days=1)

    return itinerary

def calculate_estimated_cost(destination, num_days):
    city_costs = indian_cities[destination]['costs']
    
    return {
        'budget': (city_costs['hotel']['budget'] + city_costs['food']['budget'] + city_costs['transport']['budget']) * num_days,
        'mid': (city_costs['hotel']['mid'] + city_costs['food']['mid'] + city_costs['transport']['mid']) * num_days,
        'luxury': (city_costs['hotel']['luxury'] + city_costs['food']['luxury'] + city_costs['transport']['luxury']) * num_days
    }

@app.route('/generate_itinerary', methods=['POST'])
def create_itinerary():
    data = request.json
    source = data['source']
    destination = data['destination']
    num_days = int(data['num_days'])

    if source not in indian_cities or destination not in indian_cities:
        return jsonify({"error": "Invalid source or destination"}), 400

    estimated_costs = calculate_estimated_cost(destination, num_days)
    itineraries = {
        'budget': generate_itinerary(source, destination, num_days, 'budget'),
        'mid': generate_itinerary(source, destination, num_days, 'mid'),
        'luxury': generate_itinerary(source, destination, num_days, 'luxury')
    }

    return jsonify({
        "itinerary": itineraries,
        "estimated_costs": estimated_costs
    })

@app.route('/cities', methods=['GET'])
def get_cities():
    return jsonify(list(indian_cities.keys()))

if __name__ == '__main__':
    app.run(debug=True)