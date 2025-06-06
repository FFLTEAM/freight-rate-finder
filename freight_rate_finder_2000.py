import streamlit as st
import pandas as pd
from geopy.distance import geodesic
import pydeck as pdk

st.title("Freight Rate Finder")

st.sidebar.header("Enter Filter Criteria")

# Embedded dataset
records = [

from ast import literal_eval

with open("/mnt/data/embedded_records_snippet.txt") as f:
    records = [literal_eval(line.strip()) for line in f if line.strip()]

df = pd.DataFrame(records)

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

    st.subheader("Map View of Filtered Routes")
    if not df_filtered.empty:
        route_lines = pd.DataFrame([{
            "from_lat": row.origin_lat,
            "from_lon": row.origin_lon,
            "to_lat": row.destination_lat,
            "to_lon": row.destination_lon
        } for _, row in df_filtered.iterrows()])

        layer = pdk.Layer(
            "LineLayer",
            data=route_lines,
            get_source_position='[from_lon, from_lat]',
            get_target_position='[to_lon, to_lat]',
            get_width=4,
            get_color=[0, 100, 255],
            pickable=True
        )

        view_state = pdk.ViewState(
            latitude=route_lines["from_lat"].mean(),
            longitude=route_lines["from_lon"].mean(),
            zoom=4,
            pitch=0
        )

        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

    csv = df_filtered.to_csv(index=False)
    st.download_button("Download CSV", data=csv, file_name="filtered_freight_rates.csv", mime="text/csv")

    st.markdown("---")
    st.markdown("Enter latitude and longitude for origin and/or destination.")