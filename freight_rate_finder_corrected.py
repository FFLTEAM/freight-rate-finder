
# Corrected and functional Streamlit Freight Rate Finder app
import streamlit as st
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import pydeck as pdk
import random
from datetime import datetime, timedelta

st.title("Freight Rate Finder")
st.sidebar.header("Enter Filter Criteria")

cities = [
    ("Toronto", "ON", "Canada", 43.65107, -79.347015),
    ("Montreal", "QC", "Canada", 45.501689, -73.567256),
    ("Chicago", "IL", "USA", 41.8781, -87.6298),
    ("Detroit", "MI", "USA", 42.3314, -83.0458),
    ("Monterrey", "NL", "Mexico", 25.6866, -100.3161),
    ("San Antonio", "TX", "USA", 29.4241, -98.4936),
    ("Vancouver", "BC", "Canada", 49.2827, -123.1207),
    ("Seattle", "WA", "USA", 47.6062, -122.3321),
    ("Mexico City", "CDMX", "Mexico", 19.4326, -99.1332),
    ("Guadalajara", "JAL", "Mexico", 20.6597, -103.3496)
]

city_options = [f"{c[0]}, {c[2]}" for c in cities]
service_types = ["FTL", "LTL"]
equipment_types = ["Dry Van", "Reefer", "Flatbed", "Straight Truck", "Sprinter"]
carrier_names = ["CarrierOne", "SpeedXpress", "LogiTrans", "FastFreight", "Global Haul"]

records = []
for _ in range(1000):
    origin = random.choice(cities)
    destination = random.choice(cities)
    if origin == destination:
        continue
    rate = random.randint(500, 2500)
    date_obtained = datetime.now() - timedelta(days=random.randint(0, 60))
    records.append({
        "origin_city": origin[0], "origin_state": origin[1], "origin_country": origin[2], "origin_lat": origin[3], "origin_lon": origin[4],
        "destination_city": destination[0], "destination_state": destination[1], "destination_country": destination[2], "destination_lat": destination[3], "destination_lon": destination[4],
        "service_type": random.choice(service_types),
        "equipment_type": random.choice(equipment_types),
        "carrier_name": random.choice(carrier_names),
        "rate": rate,
        "rate_date": date_obtained.strftime("%Y-%m-%d")
    })

df = pd.DataFrame(records)
df['distance_miles'] = df.apply(lambda row: geodesic((row['origin_lat'], row['origin_lon']), (row['destination_lat'], row['destination_lon'])).miles, axis=1)
df['rate_per_mile'] = (df['rate'] / df['distance_miles']).round(2)

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

st.sidebar.subheader("Origin")
origin_choice = st.sidebar.selectbox("Choose Origin (or type below)", [""] + city_options)
origin_city = origin_state = origin_country = origin_postal = ""
if origin_choice:
    origin_city, origin_country = origin_choice.split(", ")
origin_city = st.sidebar.text_input("City", value=origin_city, key="origin_city")
origin_state = st.sidebar.text_input("State/Province", key="origin_state")
origin_country = st.sidebar.text_input("Country", value=origin_country, key="origin_country")
origin_postal = st.sidebar.text_input("Zip/Postal Code", key="origin_postal")

st.sidebar.subheader("Destination")
destination_choice = st.sidebar.selectbox("Choose Destination (or type below)", [""] + city_options)
destination_city = destination_state = destination_country = destination_postal = ""
if destination_choice:
    destination_city, destination_country = destination_choice.split(", ")
destination_city = st.sidebar.text_input("City", value=destination_city, key="dest_city")
destination_state = st.sidebar.text_input("State/Province", key="dest_state")
destination_country = st.sidebar.text_input("Country", value=destination_country, key="dest_country")
destination_postal = st.sidebar.text_input("Zip/Postal Code", key="dest_postal")

radius = st.sidebar.slider("Search Radius (miles)", 1, 150, 50)
service_options = st.sidebar.multiselect("Service Type", service_types, default=service_types)
equipment_options = st.sidebar.multiselect("Equipment Type", equipment_types, default=equipment_types)

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
            df_filtered.apply(lambda row: is_within_radius((row['origin_lat'], row['origin_lon']), origin_coords), axis=1)
        ]
    if destination_coords:
        df_filtered = df_filtered[
            df_filtered.apply(lambda row: is_within_radius((row['destination_lat'], row['destination_lon']), destination_coords), axis=1)
        ]

    st.subheader("Filtered Freight Rates")
    display_cols = ['service_type', 'rate', 'rate_per_mile', 'equipment_type', 'carrier_name', 'origin_city', 'origin_state', 'origin_country', 'destination_city', 'destination_state', 'destination_country', 'distance_miles', 'rate_date']
    st.dataframe(df_filtered[display_cols])

    if not df_filtered.empty:
        st.subheader("Lane Rate Summary")
        lanes = df_filtered.groupby(['origin_city', 'destination_city', 'service_type', 'equipment_type'])['rate'].agg(['min', 'mean', 'max']).reset_index()
        lanes.columns = ['Origin', 'Destination', 'Service Type', 'Equipment Type', 'Lowest Rate', 'Average Rate', 'Highest Rate']

        st.markdown("### Lane Pricing Statistics")
        st.markdown("---")
        for equipment in lanes['Equipment Type'].unique():
            st.markdown(f"#### Equipment Type: {equipment}")
            subset = lanes[lanes['Equipment Type'] == equipment]
            st.dataframe(subset)
        st.markdown("---")

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

    csv = df_filtered[display_cols].to_csv(index=False)
    st.download_button("Download CSV", data=csv, file_name="filtered_freight_rates.csv", mime="text/csv")

    st.markdown("---")
    st.markdown("Enter a city/state/country or zip/postal to geocode origin or destination.")
