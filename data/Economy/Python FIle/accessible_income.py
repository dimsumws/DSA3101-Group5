import requests
import pandas as pd

#retrieving from public API
dataset_id = "d_0fb1c8d8f8e4f7733e0486837e54a0c7"
url = "https://data.gov.sg/api/action/datastore_search?resource_id="  + dataset_id 
        
response = requests.get(url)

#converting from json to pandas dataframe
df = pd.DataFrame(response.json()['result']['records'])

#converting to csv file
df.to_csv('data/Economy/Final/accessible_income.csv', index=False)