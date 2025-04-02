from bs4 import BeautifulSoup
import requests
import pandas as pd
import os

urls = [
    "https://www.thrill-data.com/trip-planning/crowd-calendar/universal-studios-singapore/calendar/2024",
    "https://www.thrill-data.com/trip-planning/crowd-calendar/universal-studios-singapore/calendar/2023"
]

all_data = []

def scrape_table(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table", {"class": "data-table sortable"})
        
        # Extract table headers
        headers = [th.text.strip() for th in table.find_all("th")]

        # Extract table rows
        rows = []
        for row in table.find_all("tr")[1:]:  # Skip header row
            cells = row.find_all("td")
            row_data = [cell.text.strip() for cell in cells]
            if row_data:
                rows.append(row_data)
        df = pd.DataFrame(rows, columns=headers)
        return df
    
for url in urls:
    data = scrape_table(url)
    if data is not None:
        all_data.append(data)

final_df = pd.concat(all_data, ignore_index=True)

# Convert 'Date' to proper datetime format
final_df['Date'] = pd.to_datetime(final_df['Date'], errors='coerce')

# Convert 'Prediction', 'Actual', 'Delta' to integers
def clean_minutes(value):
    return int(value.replace(" min", "").strip()) if isinstance(value, str) and "min" in value else 0

for col in ['Prediction', 'Actual', 'Delta']:
    final_df[col] = final_df[col].apply(clean_minutes)

# Ensure 'Prediction' is never negative
final_df['Prediction'] = final_df['Prediction'].apply(lambda x: max(x, 0))

# Recalculate Delta
final_df['Delta'] = final_df['Actual'] - final_df['Prediction']

# Adjust comments
def adjust_comment(delta):
    if delta == 0:
        return "Predicted"
    elif delta < 0:
        return "Over-Predicted"
    else:
        return "Under-Predicted"

final_df['Comment'] = final_df['Delta'].apply(adjust_comment)

print(final_df.head())

# Save dataset in data directory
output_folder = os.path.join(os.path.dirname(__file__), "..", "cleaned_data_2022_2025")
output_path = os.path.join(output_folder, "cleaned_crowd_prediction_accuracy_table.csv")
final_df.to_csv(output_path, index=False)