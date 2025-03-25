import requests
import pandas as pd
          
dataset_id = "d_87d4a928fbaf172af7cdd8d4254218aa"
url = "https://data.gov.sg/api/action/datastore_search?resource_id="  + dataset_id 
        
response = requests.get(url)

df = pd.DataFrame(response.json()['result']['records'])
df = df.drop(columns = ['_id'])
colnames = list(df)
colnames = colnames[1:]
df = pd.melt(df, id_vars = ['DataSeries'], value_vars = colnames, var_name = 'year_month', value_name = 'no_of_visitors')
df['DataSeries'] = df['DataSeries'].str.lstrip()
df['year_month'] = pd.to_datetime(df['year_month'], format = '%Y%b')

males_df = df[df['DataSeries'].str.contains('Males', case=False, na=False)].copy()
females_df = df[df['DataSeries'].str.contains('Females', case=False, na=False)].copy()
merged_df = pd.concat([males_df, females_df], ignore_index=True)
merged_df.columns = ['gender', 'year_month', 'no_of_visitors']
merged_df.to_csv('data/singapore_tourism_data/Final/tourism_gender.csv', index=False)

age_groups = [
    'Under 15 Years',
    '15-19 Years',
    '20-24 Years',
    '25-34 Years',
    '35-44 Years',
    '45-54 Years',
    '55-64 Years',
    '65 & Over'
]

age_groups_df = df[df['DataSeries'].isin(age_groups)].copy()
age_groups_df.columns = ['age_group', 'year_month', 'no_of_visitors']
age_groups_df.to_csv('data/singapore_tourism_data/Final/tourism_age_groups.csv', index=False)
