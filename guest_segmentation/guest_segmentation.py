#importing necessary libraries and the cleaned survey df
from cleaned_survey import df

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb

import warnings
warnings.filterwarnings('ignore')


#exploration of data
print(df.head())


#making new dataframe consisting of only variables of interest to guest segmentation
demographics = df.iloc[:,2:9]
occasion = df.iloc[:,10]
spending_cat = df.iloc[:,37]

new_df = pd.concat([demographics,occasion,spending_cat], axis = 1)
print(new_df.head())


#renaming the columns for easy access
new_df.columns = ['frequency','age','gender','monthly_income','nationality','companion','ride_intensity','occasion','spending_cat']
print(new_df.head())


#data processing and feature engineering
#mapping frequencies to rare, moderate, frequent, traveller
freq_mapping = {
    '< Once every 3 years': 'rare',
    'Once every 2-3 years': 'rare',
    'Once every year': 'moderate',
    'A few times every year': 'frequent',
    'Once every month': 'frequent',
    '> Once every month': 'frequent',
    'When on vacation': 'traveller'
}
new_df['frequency'] = new_df['frequency'].replace(freq_mapping) 

#mapping age to young, adults, middle-aged, elderly
age_mapping = {
    '<15 years old': 'young',
    '15-18 years old': 'young',
    '19-25 years old': 'adult',
    '26-35 years old': 'adult',
    '36-45 years old': 'middle-aged',
    '46-54 years old': 'middle-aged',
    '55 and above': 'elderly'
}
new_df['age'] = new_df['age'].replace(age_mapping)

#converting gender values to lower case for consistency
new_df['gender'] = new_df['gender'].str.lower()

#mapping monthly income to low, middle and high
income_mapping = {
    'No income':'low',
    'Below $2000': 'low',
    '$2,000 - $5,999': 'middle',
    '$6,000 - $9,999': 'middle',
    '$10,000 - $19,999': 'high',
    '$20,000 and above': 'high'
}
new_df['monthly_income'] = new_df['monthly_income'].replace(income_mapping)

#mapping nationality to singaporean/pr and foreigners
new_df['nationality'] = new_df['nationality'].apply(lambda x: 'foreigners' if x != 'singaporean/pr' else x)

#exploding the companion column to create separate rows for people who selected more than 1 option
companion_mapping = {
    'Couple (I go with my partner)': 'partner', 
    'Single (I go alone)': 'alone',
    'Friends': 'friends',
    'Family': 'family'
}
new_df['companion'] = new_df['companion'].str.split(", ")
new_df = new_df.explode("companion").reset_index(drop=True)
new_df['companion'] = new_df['companion'].replace(companion_mapping)

#mapping ride intensity values to low, medium, high and do not ride
intensity_mapping = {
    'Low-intensity rides': 'low',
    'Medium-intensity rides': 'medium',
    'High-intensity rides': 'high',
    'I do not go on any rides': 'do not ride'
}
new_df['ride_intensity'] = new_df['ride_intensity'].replace(intensity_mapping)

#exploding the occasion column to create separate rows for people who selected more than 1 option
occasion_mapping = {
    'Weekdays (Mondays to Thursdays)': 'weekdays',
    'For special events (eg. Halloween': 'events',
    'Evenings/Night visits (After 6pm)': 'evening visits',
    'Fridays': 'fridays',
    'Saturdays': 'saturdays',
    'Sundays': 'sundays',
    'Public Holidays': 'public holidays',
    'School Holidays': 'school holidays'
}
new_df['occasion'] = new_df['occasion'].str.split(", ")
new_df = new_df.explode("occasion").reset_index(drop=True)
new_df['occasion'] = new_df['occasion'].replace(occasion_mapping)
new_df = new_df.query("occasion != 'Christmas etc.)'")

print(new_df)


#categorising those who spend most on transport as low spenders; 
#those who spend most on f&b as average spenders;
#those who spend most on merchandise as high spenders
spender_mapping = {
    'Transportation (e.g. Parking, taxi fares etc.)': 'low spender',
    'F&B': 'average spender',
    'Merchandise': 'high spender'
}

spending_order = ['low spender', 'average spender', 'high spender']

new_df['spending_cat'] = new_df['spending_cat'].replace(spender_mapping)
new_df = new_df.rename(columns={'spending_cat':'spender_type'})
new_df['spender_type'] = pd.Categorical(new_df['spender_type'], categories=spending_order, ordered=True)

print(new_df.head())


#exploratory data visualisations of each demographic and their highest spending category
objects = []
for col in new_df.columns:
    if new_df[col].dtype == object:
        objects.append(col)

plt.subplots(figsize=(20, 25))
for i, col in enumerate(objects):
    plt.subplot(4, 2, i + 1)
    sb.countplot(x=col, hue='spender_type', data=new_df, palette='Set2')
plt.show()


#make freq_df that counts the number of spender types by frequency 
freq_order = ['rare', 'moderate', 'frequent', 'traveller']
new_df['frequency'] = pd.Categorical(new_df['frequency'], categories=freq_order, ordered=True)

freq_df = new_df.groupby('frequency')['spender_type'].value_counts().reset_index(name='No. of spender types based on frequency')
freq_df.sort_values(['spender_type', 'frequency'], inplace=True)
freq_df.reset_index(drop=True, inplace=True)

print(freq_df)


#make age_df that counts the number of spender types by age 
age_order = ['young', 'adult', 'middle-aged', 'elderly']
new_df['age'] = pd.Categorical(new_df['age'], categories=age_order, ordered=True)

age_df = new_df.groupby('age')['spender_type'].value_counts().reset_index(name='No. of spender types based on age')
age_df.sort_values(['spender_type', 'age'], inplace=True)
age_df.reset_index(drop=True, inplace=True)

print(age_df)


#make gender_df that counts the number of spender types by gender
gender_df = new_df.groupby('gender')['spender_type'].value_counts().reset_index(name='No. of spender types based on gender')
gender_df.sort_values('spender_type', inplace=True)
gender_df.reset_index(drop=True, inplace=True)

print(gender_df)


#make income_df that counts the number of spender types by monthly income
income_order = ['low', 'middle', 'high']
new_df['monthly_income'] = pd.Categorical(new_df['monthly_income'], categories=income_order, ordered=True)

income_df = new_df.groupby('monthly_income')['spender_type'].value_counts().reset_index(name='No. of spender types based on monthly income')
income_df.sort_values(['spender_type', 'monthly_income'], inplace=True)
income_df.reset_index(drop=True, inplace=True)

print(income_df)


#make nationality_df that counts the number of spender types by nationality
nationality_df = new_df.groupby('nationality')['spender_type'].value_counts().reset_index(name='No. of spender types based on nationality')
nationality_df.sort_values('spender_type', inplace=True)
nationality_df.reset_index(drop=True, inplace=True)

print(nationality_df)


#make intensity_df that counts the number of spender types by ride intensity
ride_order = ['do not ride', 'low', 'medium', 'high']
new_df['ride_intensity'] = pd.Categorical(new_df['ride_intensity'], categories=ride_order, ordered=True)

intensity_df = new_df.groupby('ride_intensity')['spender_type'].value_counts().reset_index(name='No. of spender types based on ride intensity')
intensity_df.sort_values(['spender_type', 'ride_intensity'], inplace=True)
intensity_df.reset_index(drop=True, inplace=True)

print(intensity_df)


#make companion_df that counts the number of spender types by who people go to theme parks with
companion_df = new_df.groupby('companion')['spender_type'].value_counts().reset_index(name='No. of spender types based on who they go with')
companion_df.sort_values('spender_type', inplace=True)
companion_df.reset_index(drop=True, inplace=True)

print(companion_df)


#make occasion_df that counts the number of spender types by when people go to theme parks
occasion_df = new_df.groupby('occasion')['spender_type'].value_counts().reset_index(name='No. of spender types based when they go to theme parks')
occasion_df.sort_values('spender_type', inplace=True)
occasion_df.reset_index(drop=True, inplace=True)

print(occasion_df)


#encode each categorical variable accordingly
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder

label_encoder = LabelEncoder()
onehot_encoder = OneHotEncoder(sparse_output=False, drop='first')

ordinal = ['frequency', 'age', 'monthly_income', 'ride_intensity', 'spender_type']
nominal = ['gender', 'nationality', 'companion', 'occasion']

#use label encoder for ordinal variables
for var in ordinal:
    new_df[var] = label_encoder.fit_transform(new_df[var])

#use one hot encoder for nominal variables
for var in nominal:
    var_reshaped = pd.DataFrame(new_df[var], columns=[var])
    new_df[var] = onehot_encoder.fit_transform(var_reshaped)

print(new_df.head())


#using random forest to predict spender type
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

#splitting train and test data
X = new_df.iloc[:, 0:-1]
y = new_df.iloc[:,-1]
feature_names = X.columns
X_train, X_test, y_train, y_test = train_test_split( X, y, test_size = 0.2, random_state=10)

#fitting random forest on the train data
rf = RandomForestClassifier(n_estimators=100, random_state=10)
rf.fit(X_train, y_train)

#Gini feature importance using random forest
importances = rf.feature_importances_
feature_imp = pd.DataFrame({'Feature': feature_names, 'Gini Importance': importances}).sort_values('Gini Importance', ascending=False).reset_index()
feature_imp = feature_imp.drop(['index'],axis=1)
print(feature_imp)


#permutation feature importance
from sklearn.inspection import permutation_importance

#permutation importance randomly shuffles a single feature's values and measures the resulting performance decrease
result = permutation_importance(rf, X_test, y_test, n_repeats=10, random_state=20, n_jobs=-1)
imp_df = pd.DataFrame({'Feature': feature_names, 'Permutation Importance': result.importances_mean}).sort_values('Permutation Importance', ascending=False).reset_index()
imp_df = imp_df.drop(['index'],axis=1)
print(imp_df)


#plots comparing Gini importance and permutation importance
#Gini importance plot
plt.subplot(2, 1, 1)
plt.barh(feature_imp['Feature'], feature_imp['Gini Importance'], color='skyblue')
plt.xlabel('Gini Importance')
plt.title('Feature Importance - Gini Importance')
plt.gca().invert_yaxis()  # Invert y-axis for better visualization

#permutation feature importance plot
plt.subplot(2, 1, 2)
plt.barh(imp_df['Feature'], imp_df['Permutation Importance'])
plt.xlabel('Feature')
plt.title('Permutation Feature Importance')
plt.gca().invert_yaxis()

plt.tight_layout()
plt.show()
