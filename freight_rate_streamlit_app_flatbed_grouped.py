import streamlit as st
import pandas as pd

st.set_page_config(page_title="Freight Rate Finder", layout="wide")
st.title("🚛 Freight Rate Finder")

uploaded_file = st.file_uploader("📁 Upload your ratedata.csv file", type="csv")

if uploaded_file is not None:
    try:
        preview = pd.read_csv(uploaded_file, nrows=1)
        uploaded_file.seek(0)

        parse_dates = ["Expected Ship Date"] if "Expected Ship Date" in preview.columns else []
        df = pd.read_csv(uploaded_file, parse_dates=parse_dates)

        required_columns = {
            "Origin City", "Origin State", "Origin Zip/Postal Code",
            "Destination City", "Destination State", "Destination Zip/Postal Code",
            "Currency", "Base Rate", "Equipment Type: Name",
            "Expected Ship Date", "Stops", "Carrier Name"
        }

        if not required_columns.issubset(df.columns):
            st.error("❌ Missing required columns. Please check the format of your uploaded file.")
        else:
            st.success("✅ File loaded successfully!")

            # Normalize for comparison
            df["Origin City"] = df["Origin City"].str.strip().str.lower()
            df["Destination City"] = df["Destination City"].str.strip().str.lower()
            df["Equipment Type: Name"] = df["Equipment Type: Name"].str.strip().str.lower()

            # Create a new column grouping all 'flatbed' variants
            df["Equipment Group"] = df["Equipment Type: Name"].apply(
                lambda x: "flatbed" if "flatbed" in x else x
            )

            # UI Filters
            col1, col2 = st.columns(2)
            with col1:
                selected_origin = st.selectbox(
                    "🛫 Select Origin City",
                    sorted(df["Origin City"].dropna().unique()),
                    index=0,
                    key="origin"
                )
            with col2:
                selected_destination = st.selectbox(
                    "🛬 Select Destination City",
                    sorted(df["Destination City"].dropna().unique()),
                    index=0,
                    key="destination"
                )

            # Dropdown for equipment with grouped flatbed options
            equipment_options = sorted(df["Equipment Group"].dropna().unique())
            selected_equipment = st.selectbox("🚛 Equipment Type (Flatbeds grouped)", equipment_options)

            sort_by_date = st.checkbox("🗓️ Sort by Expected Ship Date (newest first)", value=False)

            def find_best_carriers(df, origin_city, destination_city, equipment_group, max_results=10, sort_by_date=False):
                filtered = df[
                    (df["Origin City"] == origin_city) &
                    (df["Destination City"] == destination_city) &
                    (df["Equipment Group"] == equipment_group)
                ]
                if sort_by_date and "Expected Ship Date" in filtered.columns:
                    filtered = filtered.sort_values(by=["Expected Ship Date", "Base Rate"], ascending=[False, True])
                else:
                    filtered = filtered.sort_values(by="Base Rate")
                return filtered.head(max_results)

            if st.button("🔍 Find Best Carriers"):
                matches = find_best_carriers(df, selected_origin, selected_destination, selected_equipment, sort_by_date=sort_by_date)
                if matches.empty:
                    st.warning("No matching lanes found.")
                else:
                    st.write("Top Matches:")
                    st.dataframe(matches)

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("Upload a file to begin. It must contain all required freight rate columns.")