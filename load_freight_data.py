
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

def load_freight_data():
    # Step 1: Set up Google Sheets API credentials
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Step 2: Open your Google Sheet by name
    spreadsheet = client.open("RATE Data")  # Replace with your actual sheet name
    worksheet = spreadsheet.sheet1  # Or use .worksheet("Sheet1") if needed

    # Step 3: Load data into a pandas DataFrame
    df_raw = pd.DataFrame(worksheet.get_all_records())

    # Step 4: Rename and clean columns to fit tool structure
    df = df_raw.rename(columns={
        "Origin Zip/Postal Code": "Origin Zip",
        "Destination Zip/Postal Code": "Destination Zip",
        "Equipment Type: Name": "Equipment Type",
        "Expected Ship Date": "Valid From"
    })

    # Convert data types
    df["Base Rate"] = pd.to_numeric(df["Base Rate"], errors="coerce")
    df["Valid From"] = pd.to_datetime(df["Valid From"], errors="coerce")

    return df

def find_best_carriers(df, origin_city, destination_city, equipment_type, max_results=10):
    # Filter data
    filtered = df[
        (df["Origin City"].str.lower() == origin_city.lower()) &
        (df["Destination City"].str.lower() == destination_city.lower()) &
        (df["Equipment Type"].str.lower() == equipment_type.lower())
    ]

    # Sort by Base Rate and return top matches
    filtered = filtered.sort_values(by="Base Rate", ascending=True)
    return filtered.head(max_results)[["Carrier Name", "Base Rate", "Currency", "Valid From", "Equipment Type"]]

if __name__ == "__main__":
    df = load_freight_data()
    top_matches = find_best_carriers(df, origin_city="Toronto", destination_city="Chicago", equipment_type="Dry Van")
    print(top_matches)
