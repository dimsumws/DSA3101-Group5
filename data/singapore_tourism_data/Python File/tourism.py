import requests
import pandas as pd
          
dataset_id = "d_7e7b2ee60c6ffc962f80fef129cf306e"
url = "https://data.gov.sg/api/action/datastore_search?resource_id="  + dataset_id 
        
response = requests.get(url)

df = pd.DataFrame(response.json()['result']['records'])
df = df.drop(columns = ['_id'])
colnames = list(df)
colnames = colnames[1:]
df = pd.melt(df, id_vars = ['DataSeries'], value_vars = colnames, var_name = 'year_month', value_name = 'no_of_visitors')
df['DataSeries'] = df['DataSeries'].str.lstrip()
df['year_month'] = pd.to_datetime(df['year_month'], format = '%Y%b')
df.columns = ['Region/Country', 'year_month', 'no_of_visitors']

df.to_csv('data/singapore_tourism_data/Final/tourism.csv', index=False)