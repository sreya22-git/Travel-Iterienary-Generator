# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from datetime import datetime, timedelta
import csv
import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
CORS(app)

OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

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
                },
                'lat': float(row['latitude']),
                'lon': float(row['longitude'])
            }
    return cities

indian_cities = load_city_data()

def get_weather_forecast(lat, lon, date):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for forecast in data['list']:
            forecast_date = datetime.fromtimestamp(forecast['dt'])
            if forecast_date.date() == date.date():
                return {
                    'temperature': forecast['main']['temp'],
                    'description': forecast['weather'][0]['description'],
                    'icon': forecast['weather'][0]['icon']
                }
    return None

def generate_itinerary(source, destination, num_days, cost_option):
    itinerary = []
    current_date = datetime.now()

    for day in range(1, num_days + 1):
        weather = get_weather_forecast(indian_cities[destination]['lat'], indian_cities[destination]['lon'], current_date)
        daily_plan = {
            "day": day,
            "date": current_date.strftime("%Y-%m-%d"),
            "activities": random.sample(indian_cities[destination]["attractions"], 2),
            "hotel": indian_cities[destination]["hotels"][cost_option],
            "restaurant": random.choice(indian_cities[destination]["restaurants"]),
            "transport": random.choice(indian_cities[destination]["transport"]),
            "weather": weather
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