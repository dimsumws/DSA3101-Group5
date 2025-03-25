import pandas as pd
import numpy as np

df = pd.read_csv('survey_responses.csv')

# create csv for replaced labels
questions = df.columns
labels = ['timestamp', 'visited_US', 'visit_freq', 'age', 'gender', 'monthly_income', 'nationality', 'companion', 'ride_pref', 'time_in_park', 'visit_day', 'visit_reason', 'mkting_content_seen', 'mkting_content_pref', 'get_ticket', 'fee_pricing', 'queuing', 'fast_pass_worth', 'cleanliness', 'facilities', 'navigation', 'rides', 'theme', 'relavamce', 'staffing', 'friendliness', 'return_likelihood', 'concern_malfucntion', 'concern_violence', 'concern_crowd_crush', 'concern_theft', 'concern_getting_lost', 'concern_medical_access', 'concern_weather', 'concern_food_safety', 'visit_deterrents', 'attraction_decision', 'top_expense', 'hollywood', 'minion_land', 'far_far_away', 'lost_world', 'ancient_egypt', 'scifi_city', 'new_york']

lab = pd.DataFrame(list(zip(labels, questions)),columns=['label', 'question'])
lab.to_csv('labels.csv')

# renaming columns
df.columns = labels

# convert visited_US to boolean
df['visited_US'] = np.where(df['visited_US'] == 'Yes', True, False)

# standardise nationality column
df['nationality'] = (df['nationality'].str.lower()
                    .replace(['malaysia', 'china', 'myanmar'], ['malaysian', 'chinese','burmese']))

# simplify ride intensity column
df['ride_pref'] = (df['ride_pref'].str.lower()
                   .replace('i do not go on any rides', 'no_rides')
                   .str.extract(r'(\w+)'))

# change to numerical scale for concern questions
concern_cols = ['concern_malfucntion', 'concern_violence', 'concern_crowd_crush', 'concern_theft', 'concern_getting_lost', 'concern_medical_access', 'concern_weather', 'concern_food_safety']
df[concern_cols] = (df[concern_cols].replace(['1 - Not a concern at all', '5 - Very concerned'], [1, 5])
                    .astype(int))

# remove additional remarks and irrelevant values from expenditure column
df['top_expense'] = (df['top_expense'].replace('Transportation (e.g. Parking, taxi fares etc.)', 'Transportation')
                     .apply(lambda x: x if x in ['F&B','Merchandise', 'Transportation'] else pd.NA))

path_cols = ['hollywood', 'minion_land', 'far_far_away', 'lost_world', 'ancient_egypt', 'scifi_city', 'new_york']
df[path_cols] = df[path_cols].replace(['1st', '2nd', '3rd', '4th', '5th', '6th', '7th'], [1, 2, 3, 4, 5, 6, 7]).astype('Int64')

# export as csv file
df.to_csv('cleaned_survey_responses.csv')