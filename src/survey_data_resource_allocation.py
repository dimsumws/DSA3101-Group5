import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Load Survey Data

def load_data():
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, "..", "data")

    survey_file = os.path.join(data_dir, "survey_responses.csv")

    df_survey = pd.read_csv(survey_file)

    return df_survey

# Step 2: Filter for relevant columns

df_survey = load_data()
relevant_columns = [9, 10, 16, 20, 24, 25] + list(range(28, 33))
df_filtered = df_survey.iloc[:, relevant_columns]
df_filtered = df_filtered.copy()

# Step 3: Data Transformation
df_filtered.iloc[:, 0] = df_filtered.iloc[:, 0].str.split(",").apply(lambda x: [i.strip() for i in x])
df_filtered.iloc[:, 1] = df_filtered.iloc[:, 1].replace(
    to_replace=r"For special events \(.*?\)",
    value="For special events",
    regex=True
)
df_filtered.iloc[:, 1] = df_filtered.iloc[:, 1].str.split(", ").apply(lambda x: [i.strip() for i in x])

def extract_number(value):
    if isinstance(value, str):  # If it's a string, extract the number
        return int(pd.to_numeric(pd.Series(value).str.extract(r"(\d)")[0], errors='coerce'))
    return value  # If it's already a number, keep it

df_filtered.iloc[:, list(range(6, 11))] = df_filtered.iloc[:, list(range(6, 11))].applymap(extract_number)

# Step 4: Count Occurences

df_0_explode = df_filtered.explode(df_filtered.columns[0])
time_count = df_0_explode[df_filtered.columns[0]].value_counts()
time_counts_df = time_count.reset_index().rename(columns={"index": "Time Slot", df_0_explode.columns[0]: "Count"})

df_1_explode = df_filtered.explode(df_filtered.columns[1])
days_categories = df_1_explode[df_filtered.columns[1]].value_counts()
days_categories_df = days_categories.reset_index().rename(columns={"index": "Day Category", df_1_explode.columns[1]: "Count"})

numeric_columns = df_filtered.columns[2:11]
df_filtered[numeric_columns] = df_filtered[numeric_columns].apply(pd.to_numeric, errors='coerce').astype(int)

numeric_counts = {}
for col in numeric_columns:
    numeric_counts[col] = df_filtered[col].value_counts().sort_index()

rename_mapping = {
    '16. I spent less time queueing than expected': 'queue_expectation',
    '20. I was able to navigate through the theme park easily': 'ease_of_navigation',
    '24. The park was adequately staffed': 'staff_adequacy',
    '25. Staff were friendly and helpful': 'staff_friendliness_helpfulness',
    '27. How concerned are you of these possible situations at a theme park during your visit? (Rate each factor on a scale of 1-5) [Violent behaviour from others]': 'violence_concern',
    '27. How concerned are you of these possible situations at a theme park during your visit? (Rate each factor on a scale of 1-5) [Crowd crush]': 'crowd_crush_concern',
    '27. How concerned are you of these possible situations at a theme park during your visit? (Rate each factor on a scale of 1-5) [Theft & Pickpocketing]': 'theft_concern',
    '27. How concerned are you of these possible situations at a theme park during your visit? (Rate each factor on a scale of 1-5) [Getting lost or separated from friends and family]': 'getting_lost_concern',
    '27. How concerned are you of these possible situations at a theme park during your visit? (Rate each factor on a scale of 1-5) [Lack of immediate medical attention]' : 'medical_concern'
}

numeric_counts = {rename_mapping.get(k, k): v for k, v in numeric_counts.items()}
for new_name, series in numeric_counts.items():
    series.name = new_name

# Step 5: Plotting

# Plot for Time of day in which park goers normally go

fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(time_counts_df["Time Slot"], time_counts_df["Count"], color='lightcoral')
ax.set_xlabel("Time Slots", fontsize=10)
ax.set_ylabel("Count", fontsize=10)
ax.set_title("Time Slot Preferences", fontsize=12)
ax.set_xticklabels(time_counts_df["Time Slot"], rotation=45, ha="right", fontsize=9)
ax.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()

# Plot for preferred days for park goers to go

fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(days_categories_df["Day Category"], days_categories_df["Count"], color='mediumseagreen')
ax.set_xlabel("Day Categories", fontsize=10)
ax.set_ylabel("Count", fontsize=10)
ax.set_title("Day Category Preferences", fontsize=12)
ax.set_xticklabels(days_categories_df["Day Category"], rotation=45, ha="right", fontsize=9)
ax.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()

# Plot for other relevant data

# Define the number of subplots (rows & columns)
num_plots = len(numeric_counts)
cols = 3  # Number of columns (you can adjust if needed)
rows = (num_plots // cols) + (num_plots % cols > 0)  # Calculate rows dynamically

# Create a figure with multiple subplots
fig, axes = plt.subplots(rows, cols, figsize=(12, 2 * rows))
axes = axes.flatten()  # Flatten the axes array for easy iteration

for i, (category, series) in enumerate(numeric_counts.items()):
    axes[i].bar(series.index, series.values, color='skyblue')
    axes[i].set_xlabel("Rating Scale", fontsize=8)
    axes[i].set_ylabel("Count", fontsize=8)
    axes[i].set_title(category.replace("_", " ").title(), fontsize=10)
    axes[i].set_xticks(series.index)
    axes[i].tick_params(axis='both', which='major', labelsize=7)
    axes[i].grid(axis="y", linestyle="--", alpha=0.7)

# Hide any unused subplots
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

# Adjust layout for better fit
plt.tight_layout()
plt.show()