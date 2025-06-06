import streamlit as st
import pandas as pd
import numpy as np
from geopy.distance import geodesic

# Load dataset (replace this with file uploader or external CSV in production)
data = {
    'origin_city': ['Toronto', 'Detroit', 'Monterrey', 'Chicago', 'Vancouver'],
    'origin_lat': [43.65107, 42.33143, 25.68661, 41.8781, 49.2827],
    'origin_lon': [-79.347015, -83.04575, -100.31611, -87.6298, -123.1207],
    'destination_city': ['Montreal', 'Houston', 'Guadalajara', 'Los Angeles', 'Calgary'],
    'destination_lat': [45.5017, 29.7604, 20.6597, 34.0522, 51.0447],
    'destination_lon': [-73.5673, -95.3698, -103.3496, -118.2437, -114.0719],
    'country': ['Canada', 'USA', 'Mexico', 'USA', 'Canada'],
    'service_type': ['FTL', 'LTL', 'FTL', 'LTL', 'FTL'],
    'equipment_type': ['Dry Van', 'Reefer', 'Flatbed', 'Sprinter', 'Straight Truck'],
    'rate': [1200, 1500, 1800, 900, 1300]
}
df = pd.DataFrame(data)

st.title("Freight Rate Finder")

st.sidebar.header("Filter Options")

# Input location for radius filtering
latitude = st.sidebar.number_input("Enter Latitude", value=43.65)
longitude = st.sidebar.number_input("Enter Longitude", value=-79.38)
radius = st.sidebar.slider("Search Radius (miles)", min_value=1, max_value=150, value=50)

# Service Type
service_options = st.sidebar.multiselect(
    "Service Type", ['FTL', 'LTL'], default=['FTL', 'LTL']
)

# Equipment Type
equipment_options = st.sidebar.multiselect(
    "Equipment Type",
    ['Dry Van', 'Reefer', 'Flatbed', 'Straight Truck', 'Sprinter'],
    default=['Dry Van', 'Reefer', 'Flatbed', 'Straight Truck', 'Sprinter']
)

# Function to check if within radius
def is_within_radius(lat, lon, center, miles):
    return geodesic((lat, lon), center).miles <= miles

center_point = (latitude, longitude)

# Filter by location, service, and equipment
df_filtered = df[
    df['service_type'].isin(service_options) &
    df['equipment_type'].isin(equipment_options)
]
df_filtered = df_filtered[
    df_filtered.apply(
        lambda row: is_within_radius(row['origin_lat'], row['origin_lon'], center_point, radius) or
                    is_within_radius(row['destination_lat'], row['destination_lon'], center_point, radius),
        axis=1
    )
]

st.subheader("Filtered Freight Rates")
st.dataframe(df_filtered)

# Optional download button
csv = df_filtered.to_csv(index=False)
st.download_button(
    label="Download Filtered Results as CSV",
    data=csv,
    file_name='filtered_freight_rates.csv',
    mime='text/csv'
)

st.markdown("---")
st.markdown("Enter a location and radius to find freight rates near that area. You can filter by service and equipment type.")
