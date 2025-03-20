import requests
import pandas as pd

dataset_id = "d_7e7b2ee60c6ffc962f80fef129cf306e"
url = "https://data.gov.sg/api/action/datastore_search?resource_id="  + dataset_id 
        
response = requests.get(url)

df = pd.DataFrame(response.json()['result']['records'])

df.to_csv('data/Economy/Final/tourism_monthly.csv', index=False)