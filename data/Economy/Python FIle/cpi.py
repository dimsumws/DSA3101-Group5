import requests
import pandas as pd

#retrieving data
dataset_id = "d_8b007d0a630351e2375d5d574e108058"
url = "https://data.gov.sg/api/action/datastore_search?resource_id="  + dataset_id 
        
response = requests.get(url)
json = response.json()

#converting to pandas dataframe
df = pd.DataFrame(response.json()['result']['records'])

while 'next' in json['result']['_links'] and json['result']['_links']['next']:
    curr_num = df.shape[0]
    response = requests.get("https://data.gov.sg" + json['result']['_links']['next'])
    json = response.json()
    df = pd.concat([df, pd.DataFrame(json['result']['records'])], ignore_index=True)
    print(f"Current number of records fetched: {df.shape[0]}")
    if df.shape[0] == curr_num:
        break

#only selecting some years
df = df.loc[:, ['2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '_id', 'DataSeries']]

#reordering columns
df = df[['DataSeries', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']]

#saving as csv file
df.to_csv("data/Economy/Final/cpi.csv", index=False)