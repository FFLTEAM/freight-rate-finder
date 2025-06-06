
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
    # Load default dataset if no file is uploaded
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

origin_input = st.sidebar.text_input("Origin (City optional, Country required)", value="Toronto, Canada")
destination_input = st.sidebar.text_input("Destination (City optional, Country required)", value="Montreal, Canada")
radius = st.sidebar.slider("Search Radius (miles)", 1, 150, 50)

service_options = st.sidebar.multiselect("Service Type", ['FTL', 'LTL'], default=['FTL', 'LTL'])
equipment_options = st.sidebar.multiselect(
    "Equipment Type",
    ['Dry Van', 'Reefer', 'Flatbed', 'Straight Truck', 'Sprinter'],
    default=['Dry Van', 'Reefer', 'Flatbed', 'Straight Truck', 'Sprinter']
)

# Convert location string to lat/lon
def geocode_location(location_str):
    try:
        location = geolocator.geocode(location_str)
        return (location.latitude, location.longitude) if location else None
    except:
        return None

origin_coords = geocode_location(origin_input)
destination_coords = geocode_location(destination_input)

if not origin_coords and not destination_coords:
    st.error("At least one location (origin or destination) must be geocoded successfully. Please check your input.")
else:
    # Use postal codes for precise location if available
    df['origin_latlon'] = df['origin_postal'].fillna(df['origin_city'] + ", " + df['origin_country'])
    df['destination_latlon'] = df['destination_postal'].fillna(df['destination_city'] + ", " + df['destination_country'])

    df['origin_coords'] = df['origin_latlon'].apply(geocode_location)
    df['destination_coords'] = df['destination_latlon'].apply(geocode_location)

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
    st.markdown("Enter origin and/or destination using at least the country. City is optional.")
