import streamlit as st
import pandas as pd

st.set_page_config(page_title="Freight Rate Finder", layout="wide")
st.title("🚛 Freight Rate Finder")

# Upload the CSV file
uploaded_file = st.file_uploader("📁 Upload your ratedata.csv file", type="csv")

if uploaded_file is not None:
    try:
        # Read the uploaded CSV
        df = pd.read_csv(uploaded_file, parse_dates=["Valid From"], dtype={"Base Rate": float})

        # Basic field validation
        required_columns = {"Origin City", "Destination City", "Equipment Type", "Carrier Name", "Base Rate", "Currency", "Valid From"}
        if not required_columns.issubset(df.columns):
            st.error(f"Missing required columns. Your file must include: {', '.join(required_columns)}")
        else:
            st.success("✅ File loaded successfully!")

            # Input fields
            origin = st.text_input("Origin City", "Toronto")
            destination = st.text_input("Destination City", "Chicago")
            equipment = st.selectbox("Equipment Type", df["Equipment Type"].dropna().unique())

            # Filter and show best carriers
            def find_best_carriers(df, origin_city, destination_city, equipment_type, max_results=10):
                filtered = df[
                    (df["Origin City"].str.lower() == origin_city.lower()) &
                    (df["Destination City"].str.lower() == destination_city.lower()) &
                    (df["Equipment Type"].str.lower() == equipment_type.lower())
                ]
                return filtered.sort_values(by="Base Rate").head(max_results)

            if st.button("🔍 Find Best Carriers"):
                matches = find_best_carriers(df, origin, destination, equipment)
                if matches.empty:
                    st.warning("No matching lanes found.")
                else:
                    st.write("Top Matches:")
                    st.dataframe(matches)

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

else:
    st.info("Upload a file to begin. Must include columns like Origin City, Destination City, Equipment Type, etc.")