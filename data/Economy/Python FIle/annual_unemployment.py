import requests
import pandas as pd

#retrieving from public API
dataset_id = "d_e3598914c86699a9a36e68190f78c59a"
url = "https://data.gov.sg/api/action/datastore_search?resource_id="  + dataset_id 
        
response = requests.get(url)

#converting from json to pandas dataframe
df = pd.DataFrame(response.json()['result']['records'])

#converting to csv file
df.to_csv('data/Economy/Final/annual_unemployment.csv', index=False)