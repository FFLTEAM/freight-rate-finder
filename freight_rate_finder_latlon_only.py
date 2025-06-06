
import streamlit as st
import pandas as pd
from geopy.distance import geodesic

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
        'origin_lat': [43.65107, 42.33143, 25.68661, 41.8781, 49.2827],
        'origin_lon': [-79.347015, -83.04575, -100.31612, -87.6298, -123.1207],
        'destination_city': ['Montreal', 'Houston', 'Guadalajara', 'Los Angeles', 'Calgary'],
        'destination_state': ['QC', 'TX', 'JA', 'CA', 'AB'],
        'destination_country': ['Canada', 'USA', 'Mexico', 'USA', 'Canada'],
        'destination_postal': ['H2Y 1C6', '77002', '44100', '90001', 'T2P 1J9'],
        'destination_lat': [45.5017, 29.7604, 20.6597, 34.0522, 51.0447],
        'destination_lon': [-73.5673, -95.3698, -103.3496, -118.2437, -114.0719],
        'service_type': ['FTL', 'LTL', 'FTL', 'LTL', 'FTL'],
        'equipment_type': ['Dry Van', 'Reefer', 'Flatbed', 'Sprinter', 'Straight Truck'],
        'rate': [1200, 1500, 1800, 900, 1300]
    }
    df = pd.DataFrame(data)

# Origin Input
origin_lat = st.sidebar.text_input("Origin Latitude")
origin_lon = st.sidebar.text_input("Origin Longitude")

# Destination Input
destination_lat = st.sidebar.text_input("Destination Latitude")
destination_lon = st.sidebar.text_input("Destination Longitude")

radius = st.sidebar.slider("Search Radius (miles)", 1, 150, 50)

service_options = st.sidebar.multiselect("Service Type", ['FTL', 'LTL'], default=['FTL', 'LTL'])
equipment_options = st.sidebar.multiselect(
    "Equipment Type",
    ['Dry Van', 'Reefer', 'Flatbed', 'Straight Truck', 'Sprinter'],
    default=['Dry Van', 'Reefer', 'Flatbed', 'Straight Truck', 'Sprinter']
)

def is_within_radius(coords, center):
    try:
        return geodesic(coords, center).miles <= radius if coords else False
    except:
        return False

origin_coords = (float(origin_lat), float(origin_lon)) if origin_lat and origin_lon else None
destination_coords = (float(destination_lat), float(destination_lon)) if destination_lat and destination_lon else None

if not origin_coords and not destination_coords:
    st.error("Please enter at least one location (origin or destination) with latitude and longitude.")
else:
    df_filtered = df[
        df['service_type'].isin(service_options) &
        df['equipment_type'].isin(equipment_options)
    ]

    if origin_coords:
        df_filtered = df_filtered[
            df_filtered.apply(lambda row: is_within_radius((row['origin_lat'], row['origin_lon']), origin_coords) or
                                            is_within_radius((row['destination_lat'], row['destination_lon']), origin_coords), axis=1)
        ]
    elif destination_coords:
        df_filtered = df_filtered[
            df_filtered.apply(lambda row: is_within_radius((row['origin_lat'], row['origin_lon']), destination_coords) or
                                            is_within_radius((row['destination_lat'], row['destination_lon']), destination_coords), axis=1)
        ]

    st.subheader("Filtered Freight Rates")
    st.dataframe(df_filtered)

    csv = df_filtered.to_csv(index=False)
    st.download_button("Download CSV", data=csv, file_name="filtered_freight_rates.csv", mime="text/csv")

    st.markdown("---")
    st.markdown("Enter latitude and longitude for origin and/or destination.")
