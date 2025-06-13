import streamlit as st
import pandas as pd

st.set_page_config(page_title="Freight Rate Finder", layout="wide")
st.title("🚛 Freight Rate Finder")

# Upload the CSV file
uploaded_file = st.file_uploader("📁 Upload your ratedata.csv file", type="csv")

if uploaded_file is not None:
    try:
        # Peek at column headers
        preview = pd.read_csv(uploaded_file, nrows=1)
        uploaded_file.seek(0)

        # Parse dates if 'Expected Ship Date' exists
        parse_dates = ["Expected Ship Date"] if "Expected Ship Date" in preview.columns else []
        df = pd.read_csv(uploaded_file, parse_dates=parse_dates)

        # Rename columns for internal consistency
        column_mapping = {
            "Equipment Type: Name": "Equipment Type",
        }
        df.rename(columns=column_mapping, inplace=True)

        # Required columns for processing
        required_columns = {
            "Origin City", "Destination City", "Equipment Type",
            "Carrier Name", "Base Rate", "Currency", "Expected Ship Date"
        }

        if not required_columns.issubset(df.columns):
            st.error("❌ Missing required columns after mapping. Check your file.")
        else:
            st.success("✅ File loaded successfully!")

            # Inputs
            origin = st.text_input("Origin City", "Toronto")
            destination = st.text_input("Destination City", "Chicago")
            equipment = st.selectbox("Equipment Type", df["Equipment Type"].dropna().unique())
            sort_by_date = st.checkbox("🗓️ Sort by Expected Ship Date (newest first)", value=False)

            def find_best_carriers(df, origin_city, destination_city, equipment_type, max_results=10, sort_by_date=False):
                filtered = df[
                    (df["Origin City"].str.lower() == origin_city.lower()) &
                    (df["Destination City"].str.lower() == destination_city.lower()) &
                    (df["Equipment Type"].str.lower() == equipment_type.lower())
                ]
                if sort_by_date:
                    filtered = filtered.sort_values(by=["Expected Ship Date", "Base Rate"], ascending=[False, True])
                else:
                    filtered = filtered.sort_values(by="Base Rate")
                return filtered.head(max_results)

            if st.button("🔍 Find Best Carriers"):
                matches = find_best_carriers(df, origin, destination, equipment, sort_by_date=sort_by_date)
                if matches.empty:
                    st.warning("No matching lanes found.")
                else:
                    st.write("Top Matches:")
                    st.dataframe(matches)

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("Upload a file to begin. Must include appropriate column headers.")