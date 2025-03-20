import pandas as pd

def clean_japan_tourism(path):
    df = pd.read_csv(f"{path}")[369:]
    df = df.iloc[:-1, :3]
    # Change the header names
    df.rename(columns={"Visitor Arrivals to Japan by Nationality ": "year", "Unnamed: 1": "num_visitors", "Unnamed: 2": "%_change"}, inplace=True)

    # Reset the index
    df.reset_index(drop=True, inplace=True)

    # Clean the num_visitors column
    df['num_visitors'] = df['num_visitors'].str.replace('"', '').str.replace(',', '').astype(int)

    # Clean the %_change column
    df['%_change'] = df['%_change'].str.replace('%', '').astype(float)

    df.to_csv(f"japan_annual_tourism.csv", index=False)


def clean_usj_table(df):
    # Get headers
    headers = df.columns.tolist()
    headers = [int(x) for x in headers if 'Unnamed' not in x]

    # Flatten values
    flat_values = df.values.flatten().tolist()

    # Remove NaN values
    flat_values = [str(x) for x in flat_values if pd.notna(x)]
    flat_values = [x for x in flat_values if 'Worldwide' not in x]
    # Remove references like [69] from numbers
    flat_values = [x.split("[")[0] for x in flat_values]

    # Convert numeric values properly (remove commas and convert to float if applicable)
    flat_values = [int(x.replace(",", "")) if x.replace(",", "").isdigit() else x for x in flat_values]

    # Combine headers and values
    final_list = headers + flat_values[:-2]

    year = []
    attendance = []
    start, end = 2009, 2023

    for value in final_list:
        if start<= value <= end:
            year.append(value)
        else:
            attendance.append(value)
    return pd.DataFrame({"Year": year, "Attendance": attendance})


def extract_from_wikipedia(country):
    url = f"https://en.wikipedia.org/wiki/Universal_Studios_{country}"
    tables = pd.read_html(url)

    if country == "Singapore":
        attendance_df = tables[3]
        attendance_df = attendance_df.drop(columns=["Reference"])

    elif country == "Japan":
        attendance_df = tables[18]
        attendance_df = clean_usj_table(attendance_df)

    attendance_df.to_csv(f"Universal_Studios_{country}_Attendance.csv", index=False)


if __name__=="__main__":
    clean_japan_tourism("JTM_inbound_20250303eng.csv")
    extract_from_wikipedia("Singapore")
    extract_from_wikipedia("Japan")

