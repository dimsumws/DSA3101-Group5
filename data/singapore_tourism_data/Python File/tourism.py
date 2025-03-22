import requests
import pandas as pd
          
dataset_id = "d_c6d3f73a65d1fa3a92f1f4e70e619a66"
url = "https://data.gov.sg/api/action/datastore_search?resource_id="  + dataset_id 
        
response = requests.get(url)

df = pd.DataFrame(response.json()['result']['records'])
df = df.drop(columns = ['_id'])
colnames = list(df)
colnames = colnames[1:]
df = pd.melt(df, id_vars = ['DataSeries'], value_vars = colnames, var_name = 'year_month', value_name = 'no_of_visitors')

df.to_csv('data/singapore_tourism_data/Final/tourism.csv', index=False)