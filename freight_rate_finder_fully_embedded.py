
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
]

df = pd.DataFrame(records)

geolocator = Nominatim(user_agent="freight_app")

def geocode_location(city, state, country, postal):
    query = ", ".join(filter(None, [postal, city, state, country]))
    try:
        location = geolocator.geocode(query)
        if location:
            return (location.latitude, location.longitude)
    except:
        pass
    return None

# Origin Input
st.sidebar.subheader("Origin")
origin_city = st.sidebar.text_input("City", key="origin_city")
origin_state = st.sidebar.text_input("State/Province", key="origin_state")
origin_country = st.sidebar.text_input("Country", key="origin_country")
origin_postal = st.sidebar.text_input("Zip/Postal Code", key="origin_postal")

# Destination Input
st.sidebar.subheader("Destination")
destination_city = st.sidebar.text_input("City", key="dest_city")
destination_state = st.sidebar.text_input("State/Province", key="dest_state")
destination_country = st.sidebar.text_input("Country", key="dest_country")
destination_postal = st.sidebar.text_input("Zip/Postal Code", key="dest_postal")

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

origin_coords = geocode_location(origin_city, origin_state, origin_country, origin_postal) if any([origin_city, origin_state, origin_country, origin_postal]) else None
destination_coords = geocode_location(destination_city, destination_state, destination_country, destination_postal) if any([destination_city, destination_state, destination_country, destination_postal]) else None

if not origin_coords and not destination_coords:
    st.error("Please enter at least one location (origin or destination) with city/state/country or zip/postal code.")
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
    st.markdown("Enter a city/state/country or zip/postal to geocode origin or destination.")
