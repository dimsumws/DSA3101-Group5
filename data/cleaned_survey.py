import numpy as np
import pandas as pd

df = pd.read_csv('survey_responses.csv')

#filter for those that have been to universal studios
df = df[df.iloc[:,1] == "Yes"]

#clean inconsistent data entries under the nationality column
df.iloc[:,6] = (df.iloc[:,6].str.lower()
                .replace('malaysia' , 'malaysian')
                .replace('china', 'chinese')
                .replace('myanmar','burmese'))

#clean inconsistent data entry under factors dissuading theme park visits column
df.iloc[:,35] = df.iloc[:,35].replace('Price', 'Costs (F&B, admission tickets, etc.)')

#replace invalid data entries with NA
def replace_with_na(col, valid_entries):
    for entry in col:
        if (entry not in valid_entries):
            col = col.replace(entry, np.nan)
    return col

#replace invalid data entries in spending category column with NA
df.iloc[:,37] = replace_with_na(df.iloc[:,37], ['F&B','Merchandise', 'Transportation (e.g. Parking, taxi fares etc.)'])

