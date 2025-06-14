
import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    return pd.read_csv("freight_rates.csv")

df = load_data()

# Add computed column for Suggested Buy Rate (20% markup assumption)
df["Suggested Buy Rate"] = df["Carrier Total (converted)"] / 1.20
df["Profit"] = df["Carrier Total (converted)"] - df["Suggested Buy Rate"]

st.title("🚛 Freight Rate Finder")
st.markdown("Filter historical rates by Mode Type, Origin, Destination, and Equipment Type.")

# Required filter
mode_types = sorted(df["-Mode Type"].dropna().unique())
selected_mode = st.selectbox("Select Mode Type (Required)", mode_types)

# Optional filters
origin_city = st.text_input("Origin City (optional)")
destination_city = st.text_input("Destination City (optional)")
equipment_type = st.text_input("Equipment Type (optional)")

# Apply filters
if selected_mode:
    filtered_df = df[df["-Mode Type"] == selected_mode]

    if origin_city:
        filtered_df = filtered_df[filtered_df["Origin City"].str.contains(origin_city, case=False, na=False)]
    if destination_city:
        filtered_df = filtered_df[filtered_df["Destination City"].str.contains(destination_city, case=False, na=False)]
    if equipment_type:
        filtered_df = filtered_df[filtered_df["Equipment Type: Name"].str.contains(equipment_type, case=False, na=False)]

    st.success(f"Found {len(filtered_df)} matching record(s).")
    st.dataframe(filtered_df[[
        "Origin City", "Destination City", "Equipment Type: Name",
        "-Mode Type", "Carrier Total (converted)",
        "Suggested Buy Rate", "Profit"
    ]])
else:
    st.warning("⚠️ Please select a Mode Type to see matching rates.")
