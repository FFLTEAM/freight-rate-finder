import os
import pandas as pd

def load_freight_data_local():
    # Construct the universal path to ~/rates/ratedata.csv
    home_dir = os.path.expanduser("~")
    csv_path = os.path.join(home_dir, "rates", "ratedata.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")

    # Load the CSV into a DataFrame
    df = pd.read_csv(csv_path, parse_dates=["Valid From"], dtype={"Base Rate": float})
    return df

def find_best_carriers(df, origin_city, destination_city, equipment_type, max_results=10):
    filtered = df[
        (df["Origin City"].str.lower() == origin_city.lower()) &
        (df["Destination City"].str.lower() == destination_city.lower()) &
        (df["Equipment Type"].str.lower() == equipment_type.lower())
    ]
    filtered = filtered.sort_values(by="Base Rate", ascending=True)
    return filtered.head(max_results)[["Carrier Name", "Base Rate", "Currency", "Valid From", "Equipment Type"]]

if __name__ == "__main__":
    df = load_freight_data_local()
    top_matches = find_best_carriers(df, origin_city="Toronto", destination_city="Chicago", equipment_type="Dry Van")
    print(top_matches)