import pandas as pd

def clean_japan_tourism(path):
    df = pd.read_csv(f"{path}")[369:]
    df = df.iloc[:-1, :3]
    # Change the header names
    df.rename(columns={"Visitor Arrivals to Japan by Nationality ": "Year", "Unnamed: 1": "num_visitors", "Unnamed: 2": "YoY_Change"}, inplace=True)

    # Reset the index
    df.reset_index(drop=True, inplace=True)

    # Clean the num_visitors column
    df['num_visitors'] = df['num_visitors'].str.replace('"', '').str.replace(',', '').astype(int)

    # Clean the %_change column
    df['YoY_Change'] = df['YoY_Change'].str.replace('%', '').astype(float)

    df.to_csv(f"Japan_Annual_Tourism.csv", index=False)


def clean_table(df, start, end, offset):
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
    final_list = headers + flat_values[:-offset]

    year = []
    attendance = []

    for value in final_list:
        if start<= value <= end:
            year.append(value)
        else:
            attendance.append(value)
    return pd.DataFrame({"Year": year, "Attendance": attendance})


def extract_from_wikipedia(park, country):
    if park == "Universal Studios":
        url = f"https://en.wikipedia.org/wiki/Universal_Studios_{country}"
        tables = pd.read_html(url)

        if country == "Singapore":
            attendance_df = tables[3]
            attendance_df = attendance_df.drop(columns=["Reference"])

        elif country == "Japan":
            attendance_df = tables[18]
            attendance_df = clean_table(attendance_df, 2009, 2023, 2)

        attendance_df.to_csv(f"Universal_Studios_{country}_Attendance.csv", index=False)
    
    else:
        url = "https://en.wikipedia.org/wiki/Tokyo_Disneyland"
        table = pd.read_html(url)
        attendance_df = table[2]
        attendance_df = clean_table(attendance_df, 2006, 2023, 1)
    
        attendance_df.to_csv(f"Disney_{country}_Attendance.csv", index=False)
        


if __name__=="__main__":
    clean_japan_tourism("JTM_inbound_20250303eng.csv")
    extract_from_wikipedia("Universal Studios", "Singapore")
    extract_from_wikipedia("Universal Studios", "Japan")
    extract_from_wikipedia("Disney", "Japan")
