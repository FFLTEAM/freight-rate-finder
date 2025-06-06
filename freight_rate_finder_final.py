
import streamlit as st
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import pydeck as pdk

st.title("Freight Rate Finder")

st.sidebar.header("Enter Filter Criteria")

# Embedded dataset
records = [
    {"origin_city": "Toronto", "origin_state": "ON", "origin_country": "Canada", "origin_lat": 43.65107, "origin_lon": -79.347015, "destination_city": "Montreal", "destination_state": "QC", "destination_country": "Canada", "destination_lat": 45.501689, "destination_lon": -73.567256, "service_type": "FTL", "equipment_type": "Dry Van", "rate": 1200},
    {"origin_city": "Chicago", "origin_state": "IL", "origin_country": "USA", "origin_lat": 41.8781, "origin_lon": -87.6298, "destination_city": "Detroit", "destination_state": "MI", "destination_country": "USA", "destination_lat": 42.3314, "destination_lon": -83.0458, "service_type": "LTL", "equipment_type": "Reefer", "rate": 900},
    {"origin_city": "Monterrey", "origin_state": "NL", "origin_country": "Mexico", "origin_lat": 25.6866, "origin_lon": -100.3161, "destination_city": "San Antonio", "destination_state": "TX", "destination_country": "USA", "destination_lat": 29.4241, "destination_lon": -98.4936, "service_type": "FTL", "equipment_type": "Flatbed", "rate": 1500},
    {"origin_city": "Vancouver", "origin_state": "BC", "origin_country": "Canada", "origin_lat": 49.2827, "origin_lon": -123.1207, "destination_city": "Seattle", "destination_state": "WA", "destination_country": "USA", "destination_lat": 47.6062, "destination_lon": -122.3321, "service_type": "LTL", "equipment_type": "Sprinter", "rate": 700},
    {"origin_city": "Mexico City", "origin_state": "CDMX", "origin_country": "Mexico", "origin_lat": 19.4326, "origin_lon": -99.1332, "destination_city": "Guadalajara", "destination_state": "JAL", "destination_country": "Mexico", "destination_lat": 20.6597, "destination_lon": -103.3496, "service_type": "FTL", "equipment_type": "Straight Truck", "rate": 1100},
    {"origin_city": "Los Angeles", "origin_state": "CA", "origin_country": "USA", "origin_lat": 34.0522, "origin_lon": -118.2437, "destination_city": "Phoenix", "destination_state": "AZ", "destination_country": "USA", "destination_lat": 33.4484, "destination_lon": -112.074, "service_type": "FTL", "equipment_type": "Dry Van", "rate": 1300},
    {"origin_city": "New York", "origin_state": "NY", "origin_country": "USA", "origin_lat": 40.7128, "origin_lon": -74.006, "destination_city": "Boston", "destination_state": "MA", "destination_country": "USA", "destination_lat": 42.3601, "destination_lon": -71.0589, "service_type": "LTL", "equipment_type": "Reefer", "rate": 850},
    {"origin_city": "Calgary", "origin_state": "AB", "origin_country": "Canada", "origin_lat": 51.0447, "origin_lon": -114.0719, "destination_city": "Edmonton", "destination_state": "AB", "destination_country": "Canada", "destination_lat": 53.5461, "destination_lon": -113.4938, "service_type": "FTL", "equipment_type": "Flatbed", "rate": 950},
    {"origin_city": "Houston", "origin_state": "TX", "origin_country": "USA", "origin_lat": 29.7604, "origin_lon": -95.3698, "destination_city": "Dallas", "destination_state": "TX", "destination_country": "USA", "destination_lat": 32.7767, "destination_lon": -96.797, "service_type": "LTL", "equipment_type": "Straight Truck", "rate": 800},
    {"origin_city": "Tijuana", "origin_state": "BC", "origin_country": "Mexico", "origin_lat": 32.5149, "origin_lon": -117.0382, "destination_city": "San Diego", "destination_state": "CA", "destination_country": "USA", "destination_lat": 32.7157, "destination_lon": -117.1611, "service_type": "FTL", "equipment_type": "Sprinter", "rate": 600}
]

# Save script to .py file
path = "/mnt/data/freight_rate_finder_final.py"
Path(path).write_text(full_script)
path
