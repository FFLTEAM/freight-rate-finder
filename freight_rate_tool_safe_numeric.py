
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Freight Rate Finder", layout="wide")
st.title("Freight Rate Finder")

uploaded_file = st.file_uploader("📁 Upload your rate data CSV", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Normalize column headers
        df.columns = [col.strip() for col in df.columns]

        # Column aliasing for flexibility
        column_aliases = {
            "Carrier Total (converted)": "Base Rate",
        }
        for original, alias in column_aliases.items():
            if original in df.columns and alias not in df.columns:
                df[alias] = df[original]

        # Re-check required columns after aliasing
        required_columns = {
            "Origin City", "Origin State", "Origin Country", "Origin Zip/Postal Code",
            "Destination City", "Destination State", "Destination Country", "Destination Zip/Postal Code",
            "Currency", "Base Rate", "Equipment Type: Name",
            "Expected Ship Date", "Carrier Service: Name", "-Mode Type",
            "Load Number", "Stops"
        }

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"❌ Missing required column(s): {', '.join(missing_columns)}")
            st.stop()

        st.success("✅ File loaded successfully!")

        # Clean lowercase inputs
        for col in ["Origin City", "Destination City", "Origin State", "Destination State", "Equipment Type: Name", "-Mode Type"]:
            df[col] = df[col].astype(str).str.strip().str.lower()

        df["Equipment Group"] = df["Equipment Type: Name"].apply(
            lambda x: "flatbed" if "flatbed" in str(x) else x
        )

        # ✅ Safely convert Base Rate to numeric
        df["Base Rate"] = pd.to_numeric(df["Base Rate"].astype(str).str.replace('[^0-9.]', '', regex=True), errors='coerce')

        # Drop rows where Base Rate is not valid
        df = df[df["Base Rate"].notna()]

        # Suggested Buy Rate and Profit
        df["Suggested Buy Rate"] = df["Base Rate"] / 1.20
        df["Profit (Est.)"] = df["Base Rate"] - df["Suggested Buy Rate"]

        st.sidebar.markdown("🚚 **Select Mode Type**")
        mode_types = sorted(df["-Mode Type"].dropna().unique())
        selected_mode = st.sidebar.selectbox("Mode Type (required)", mode_types)

        if not selected_mode:
            st.warning("⚠️ Please select a Mode Type to begin filtering.")
            st.stop()

        df = df[df["-Mode Type"] == selected_mode]

        filter_mode = st.radio("🔍 Choose Pairing Mode", ["City Pairing", "State Pairing"])

        if filter_mode == "State Pairing":
            col1, col2 = st.columns(2)
            origin_states = sorted(df["Origin State"].dropna().unique())
            selected_origin_state = col1.selectbox("🗺️ Origin State", origin_states)

            dest_states = sorted(df[df["Origin State"] == selected_origin_state]["Destination State"].dropna().unique())
            selected_destination_state = col2.selectbox("🗺️ Destination State", dest_states)

            df_filtered = df[
                (df["Origin State"] == selected_origin_state) &
                (df["Destination State"] == selected_destination_state)
            ]
        else:
            col1, col2 = st.columns(2)
            origin_cities = sorted(df["Origin City"].dropna().unique())
            selected_origin_city = col1.selectbox("🛫 Origin City", origin_cities)

            destination_cities = sorted(df[df["Origin City"] == selected_origin_city]["Destination City"].dropna().unique())
            selected_destination_city = col2.selectbox("🛬 Destination City", destination_cities)

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
            if sort_by_date:
                filtered_df = filtered_df.sort_values(by=["Expected Ship Date", "Base Rate"], ascending=[False, True])
            else:
                filtered_df = filtered_df.sort_values(by="Base Rate")
            return filtered_df.head(max_results)

        if st.button("🔍 Find Best Carriers"):
            matches = find_best_carriers(df_filtered, selected_equipment, sort_by_date=sort_by_date)
            if matches.empty:
                st.warning("No matching lanes found.")
            else:
                st.write("Top Matches (based on Base Rate):")
                st.dataframe(matches[[
                    "Origin City", "Destination City", "Base Rate",
                    "Suggested Buy Rate", "Profit (Est.)", "Equipment Group",
                    "Carrier Service: Name", "Expected Ship Date"
                ]])

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("Upload a file to begin. It must contain all required freight rate columns.")
