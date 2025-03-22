import requests
import pandas as pd

dataset_id = "d_f5d4dc45fc7b6c682de716d2aa6c85d7"
url = "https://data.gov.sg/api/action/datastore_search?resource_id="  + dataset_id 
        
response = requests.get(url)
json = response.json()
total = json['result']['total']

df = pd.DataFrame(response.json()['result']['records'])

while 'next' in json['result']['_links'] and json['result']['_links']['next']:
    curr_num = df.shape[0]
    response = requests.get("https://data.gov.sg" + json['result']['_links']['next'])
    json = response.json()
    df = pd.concat([df, pd.DataFrame(json['result']['records'])], ignore_index=True)
    if df.shape[0] == curr_num:
        break

df.to_csv('data/Economy/Final/employment_industry.csv', index=False)

print("employment_industry.py has been executed successfully")