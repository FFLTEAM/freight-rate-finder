import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Freight Rate Finder", layout="wide")
st.title("Freight Rate Finder")

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

            for col in ["Origin City", "Destination City", "Origin State", "Destination State", "Equipment Type: Name"]:
                df[col] = df[col].astype(str).str.strip().str.lower()

            df["Equipment Group"] = df["Equipment Type: Name"].apply(
                lambda x: "flatbed" if "flatbed" in str(x) else x
            )

            # Radius filter UI (placeholder, not active)
            st.sidebar.markdown("📍 **Radius Filter**")
            st.sidebar.slider("Max Radius from Origin (miles)", 0, 150, 50)

            # Choose filter mode
            filter_mode = st.radio("🔍 Choose Pairing Mode", ["City Pairing", "State Pairing"])

            if filter_mode == "State Pairing":
                col_state1, col_state2 = st.columns(2)
                origin_states = sorted(df["Origin State"].dropna().unique())
                selected_origin_state = col_state1.selectbox("🗺️ Origin State", origin_states)

                dest_states = sorted(df[df["Origin State"] == selected_origin_state]["Destination State"].dropna().unique())
                selected_destination_state = col_state2.selectbox("🗺️ Destination State", dest_states)

                df_filtered = df[
                    (df["Origin State"] == selected_origin_state) &
                    (df["Destination State"] == selected_destination_state)
                ]

            else:
                col_city1, col_city2 = st.columns(2)
                origin_cities = sorted(df["Origin City"].dropna().unique())
                selected_origin_city = col_city1.selectbox("🛫 Origin City", origin_cities)

                destination_cities = sorted(df[df["Origin City"] == selected_origin_city]["Destination City"].dropna().unique())
                selected_destination_city = col_city2.selectbox("🛬 Destination City", destination_cities)

                df_filtered = df[
                    (df["Origin City"] == selected_origin_city) &
                    (df["Destination City"] == selected_destination_city)
                ]

            equipment_options = ["all equipment"] + sorted(df["Equipment Group"].dropna().unique())
            selected_equipment = st.selectbox("🚛 Equipment Type (Flatbeds grouped)", equipment_options)

            sort_by_date = st.checkbox("🗓️ Sort by Expected Ship Date (newest first)", value=False)

            def find_best_carriers(filtered_df, equipment_group, max_results=10, sort_by_date=False):
                if equipment_group != "all equipment":
                    filtered_df = filtered_df[filtered_df["Equipment Group"] == equipment_group]
                if sort_by_date and "Expected Ship Date" in filtered_df.columns:
                    filtered_df = filtered_df.sort_values(by=["Expected Ship Date", "Base Rate"], ascending=[False, True])
                else:
                    filtered_df = filtered_df.sort_values(by="Base Rate")
                return filtered_df.head(max_results)

            if st.button("🔍 Find Best Carriers"):
                matches = find_best_carriers(df_filtered, selected_equipment, sort_by_date=sort_by_date)
                if matches.empty:
                    st.warning("No matching lanes found.")
                else:
                    st.write("Top Matches:")
                    st.dataframe(matches)

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("Upload a file to begin. It must contain all required freight rate columns.")