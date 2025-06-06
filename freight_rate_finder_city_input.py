
import streamlit as st
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

# Initialize geocoder
geolocator = Nominatim(user_agent="freight_app")

# Load dataset (mock data, replace with real dataset or CSV uploader)
data = {
    'origin_city': ['Toronto', 'Detroit', 'Monterrey', 'Chicago', 'Vancouver'],
    'origin_state': ['ON', 'MI', 'NL', 'IL', 'BC'],
    'origin_country': ['Canada', 'USA', 'Mexico', 'USA', 'Canada'],
    'destination_city': ['Montreal', 'Houston', 'Guadalajara', 'Los Angeles', 'Calgary'],
    'destination_state': ['QC', 'TX', 'JA', 'CA', 'AB'],
    'destination_country': ['Canada', 'USA', 'Mexico', 'USA', 'Canada'],
    'service_type': ['FTL', 'LTL', 'FTL', 'LTL', 'FTL'],
    'equipment_type': ['Dry Van', 'Reefer', 'Flatbed', 'Sprinter', 'Straight Truck'],
    'rate': [1200, 1500, 1800, 900, 1300]
}
df = pd.DataFrame(data)

st.title("Freight Rate Finder")

st.sidebar.header("Enter Filter Criteria")

origin_input = st.sidebar.text_input("Origin (City, State, Country)", value="Toronto, ON, Canada")
destination_input = st.sidebar.text_input("Destination (City, State, Country)", value="Montreal, QC, Canada")
radius = st.sidebar.slider("Search Radius (miles)", 1, 150, 50)

service_options = st.sidebar.multiselect("Service Type", ['FTL', 'LTL'], default=['FTL', 'LTL'])
equipment_options = st.sidebar.multiselect(
    "Equipment Type",
    ['Dry Van', 'Reefer', 'Flatbed', 'Straight Truck', 'Sprinter'],
    default=['Dry Van', 'Reefer', 'Flatbed', 'Straight Truck', 'Sprinter']
)

# Convert city/state/country to lat/lon
def geocode_location(location_str):
    try:
        location = geolocator.geocode(location_str)
        return (location.latitude, location.longitude) if location else None
    except:
        return None

origin_coords = geocode_location(origin_input)
destination_coords = geocode_location(destination_input)

if not origin_coords or not destination_coords:
    st.error("One or both locations could not be geocoded. Please check your entries.")
else:
    # Fake lat/lon columns for filtering (replace with real lat/lon if available)
    df['origin_latlon'] = df['origin_city'] + ", " + df['origin_state'] + ", " + df['origin_country']
    df['destination_latlon'] = df['destination_city'] + ", " + df['destination_state'] + ", " + df['destination_country']

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

    df_filtered = df_filtered[
        df_filtered.apply(
            lambda row: is_within_radius(row['origin_coords'], origin_coords) or
                        is_within_radius(row['destination_coords'], destination_coords),
            axis=1
        )
    ]

    st.subheader("Filtered Freight Rates")
    st.dataframe(df_filtered.drop(columns=['origin_latlon', 'destination_latlon', 'origin_coords', 'destination_coords']))

    csv = df_filtered.to_csv(index=False)
    st.download_button("Download CSV", data=csv, file_name="filtered_freight_rates.csv", mime="text/csv")

    st.markdown("---")
    st.markdown("Enter origin and destination as city/state/country to find matching freight lanes.")
