
import streamlit as st
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

# Initialize geocoder
geolocator = Nominatim(user_agent="freight_app")

st.title("Freight Rate Finder")

st.sidebar.header("Enter Filter Criteria")

# File uploader for custom datasets
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    data = {
        'origin_city': ['Toronto', 'Detroit', 'Monterrey', 'Chicago', 'Vancouver'],
        'origin_state': ['ON', 'MI', 'NL', 'IL', 'BC'],
        'origin_country': ['Canada', 'USA', 'Mexico', 'USA', 'Canada'],
        'origin_postal': ['M5H 2N2', '48226', '64000', '60601', 'V6B 2Y5'],
        'destination_city': ['Montreal', 'Houston', 'Guadalajara', 'Los Angeles', 'Calgary'],
        'destination_state': ['QC', 'TX', 'JA', 'CA', 'AB'],
        'destination_country': ['Canada', 'USA', 'Mexico', 'USA', 'Canada'],
        'destination_postal': ['H2Y 1C6', '77002', '44100', '90001', 'T2P 1J9'],
        'service_type': ['FTL', 'LTL', 'FTL', 'LTL', 'FTL'],
        'equipment_type': ['Dry Van', 'Reefer', 'Flatbed', 'Sprinter', 'Straight Truck'],
        'rate': [1200, 1500, 1800, 900, 1300]
    }
    df = pd.DataFrame(data)

# Origin Input
origin_postal = st.sidebar.text_input("Origin ZIP/Postal Code")
origin_city = st.sidebar.text_input("Origin City")
origin_state = st.sidebar.text_input("Origin State/Province")
origin_country = st.sidebar.text_input("Origin Country", value="Canada")

# Destination Input
destination_postal = st.sidebar.text_input("Destination ZIP/Postal Code")
destination_city = st.sidebar.text_input("Destination City")
destination_state = st.sidebar.text_input("Destination State/Province")
destination_country = st.sidebar.text_input("Destination Country", value="Canada")

radius = st.sidebar.slider("Search Radius (miles)", 1, 150, 50)

service_options = st.sidebar.multiselect("Service Type", ['FTL', 'LTL'], default=['FTL', 'LTL'])
equipment_options = st.sidebar.multiselect(
    "Equipment Type",
    ['Dry Van', 'Reefer', 'Flatbed', 'Straight Truck', 'Sprinter'],
    default=['Dry Van', 'Reefer', 'Flatbed', 'Straight Truck', 'Sprinter']
)

# Geocode using ZIP/postal if provided; otherwise use city/state/country

def geocode_from_inputs(postal, city, state, country):
    if postal:
        return geolocator.geocode(postal + ", " + country)
    elif city and state and country:
        return geolocator.geocode(city + ", " + state + ", " + country)
    return None

origin_location = geocode_from_inputs(origin_postal.strip(), origin_city.strip(), origin_state.strip(), origin_country.strip())
destination_location = geocode_from_inputs(destination_postal.strip(), destination_city.strip(), destination_state.strip(), destination_country.strip())

origin_coords = (origin_location.latitude, origin_location.longitude) if origin_location else None
destination_coords = (destination_location.latitude, destination_location.longitude) if destination_location else None

if not origin_coords and not destination_coords:
    st.error("You must provide either a ZIP/postal code or a full city, state, and country for origin or destination.")
else:
    df['origin_latlon'] = df['origin_postal'].fillna(df['origin_city'] + ", " + df['origin_country'])
    df['destination_latlon'] = df['destination_postal'].fillna(df['destination_city'] + ", " + df['destination_country'])

    def safe_geocode(loc):
        try:
            g = geolocator.geocode(loc)
            return (g.latitude, g.longitude) if g else None
        except:
            return None

    df['origin_coords'] = df['origin_latlon'].apply(safe_geocode)
    df['destination_coords'] = df['destination_latlon'].apply(safe_geocode)

    def is_within_radius(coords, center):
        try:
            return geodesic(coords, center).miles <= radius if coords else False
        except:
            return False

    df_filtered = df[
        df['service_type'].isin(service_options) &
        df['equipment_type'].isin(equipment_options)
    ]

    if origin_coords:
        df_filtered = df_filtered[
            df_filtered['origin_coords'].apply(lambda x: is_within_radius(x, origin_coords)) |
            (df_filtered['destination_coords'].apply(lambda x: is_within_radius(x, origin_coords)) if destination_coords else False)
        ]
    elif destination_coords:
        df_filtered = df_filtered[
            df_filtered['origin_coords'].apply(lambda x: is_within_radius(x, destination_coords)) |
            df_filtered['destination_coords'].apply(lambda x: is_within_radius(x, destination_coords))
        ]

    st.subheader("Filtered Freight Rates")
    st.dataframe(df_filtered.drop(columns=['origin_latlon', 'destination_latlon', 'origin_coords', 'destination_coords']))

    csv = df_filtered.to_csv(index=False)
    st.download_button("Download CSV", data=csv, file_name="filtered_freight_rates.csv", mime="text/csv")

    st.markdown("---")
    st.markdown("Enter either ZIP/postal OR city + state + country for origin and/or destination.")
