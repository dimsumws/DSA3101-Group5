import pandas as pd 
import numpy as np 
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("../data/survey_responses/cleaned_survey_responses.csv")
scale_qns = df.iloc[:, 15:27]
scale_qns.head()

summary = scale_qns.describe()
summary.loc[['mean', 'std']] = summary.loc[['mean', 'std']].round(0)
summary


# Visualising Scale Distribution


plt.figure(figsize=(12, 8))

sns.boxplot(data=scale_qns)

plt.title("Distribution of Likert Scale Responses (Mean and Quartiles) for Each Question")
plt.xlabel("Questions")
plt.xticks(rotation=45)
plt.ylabel("Likert Scale (1 to 7)")

plt.show()


# Net Promoter Score

loyalty = df.iloc[:, 27]
nps_question = df.columns[27]

promoters = (loyalty >= 6).sum()
passives = ((loyalty >= 4) & (loyalty <= 5)).sum()
detractors = (loyalty <= 3).sum()

total = loyalty.count()

promoter_pct = (promoters / total) * 100
detractor_pct = (detractors / total) * 100
nps_score = round(promoter_pct - detractor_pct)

print(nps_question)
print(f"NPS Score: {nps_score}")



# Customer Satsifaction Score

scale_qns = scale_qns.apply(pd.to_numeric, errors='coerce')  

satisfied = scale_qns.apply(lambda x: (x >= 5).sum(), axis=0) 

csat_score = (satisfied / total) * 100
csat_score = csat_score.round(0)


print(csat_score)


# Qualitative Responses

visit_deterrents = df["visit_deterrents"]
deterrent_options = ["Crowd", "Costs", "Long wait time", "Unpredictable weather conditions", "Boring"]

deterrents_count = {option: 0 for option in deterrent_options}

# Count occurrences of each deterrent word
for deterrent in deterrent_options:
    deterrents_count[deterrent] = visit_deterrents.str.contains(deterrent, case=False, na=False).sum()

total_responses = visit_deterrents.count()
deterrents_percentage = {deterrent: (count / total_responses) * 100 for deterrent, count in deterrents_count.items()}

# Convert the dictionary to a Pandas Series for easier plotting
deterrents_percentage_series = pd.Series(deterrents_percentage)

# Plot the bar chart
plt.figure(figsize=(8, 5))
deterrents_percentage_series.plot(kind='bar', color='orange', edgecolor='orange')

# Adding labels and title
plt.xlabel("Visit Deterrents")
plt.ylabel("Percentage of Responses (%)")
plt.title("Percentage of Visit Deterrents Selected")
plt.xticks(rotation=45)
plt.show()
