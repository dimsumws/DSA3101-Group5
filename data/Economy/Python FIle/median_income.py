import requests
import pandas as pd

dataset_id = "d_7b5fd60b047a80da91d2adb86cf47628"
url = "https://data.gov.sg/api/action/datastore_search?resource_id="  + dataset_id 
        
response = requests.get(url)

df = pd.DataFrame(response.json()['result']['records'])

df.to_csv('data/Economy/Final/median_income.csv', index=False)