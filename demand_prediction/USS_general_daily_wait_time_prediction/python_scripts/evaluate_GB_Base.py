import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
from math import sqrt
from sklearn.feature_extraction.text import TfidfVectorizer

## Testing this on real world labelled data from 2022 28 Dec to 2025.

# Lloading csv fils
wait_times_df = pd.read_csv("../../../data/uss_wait_times/augmented_wait_time_data/2017_to_2025_synthetic_wait_times_final.csv")
weather_df = pd.read_csv("../../../data/Meteorological/datasets/final_data/merged_weather_data_clean.csv")
school_holidays_df = pd.read_csv("../../../data/Events/Holidays/datasets/daily_school_holidays_combined_updated.csv")
events_df = pd.read_csv("../../../data/Events/EventData/supplementary_event_data_2016_2025.csv")

wait_times_df['Date'] = pd.to_datetime(wait_times_df['Date'])
weather_df['date'] = pd.to_datetime(weather_df['date'], format='%d/%m/%Y')
school_holidays_df['date'] = pd.to_datetime(school_holidays_df['date'], format='%d/%m/%Y')
events_df['Date'] = pd.to_datetime(events_df['Date'], dayfirst=True, errors='coerce')
events_df = events_df.dropna(subset=['Date'])

df = wait_times_df.copy()
df = df.merge(weather_df, left_on='Date', right_on='date', how='left')
df = df.merge(school_holidays_df[['date', 'holiday_flag']], left_on='Date', right_on='date', how='left')
df = df.merge(events_df.drop(columns=['Event_Description']), on='Date', how='left')
if 'date' in df.columns:
    df.drop(columns=['date'], inplace=True)

df['day_of_week'] = df['Date'].dt.dayofweek
weekday_ohe = pd.get_dummies(df['day_of_week'], prefix='weekday')
df = pd.concat([df, weekday_ohe], axis=1)
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
df.drop(columns=['day_of_week'], inplace=True)

non_datetime_cols = df.select_dtypes(exclude=['datetime']).columns
df[non_datetime_cols] = df[non_datetime_cols].fillna(0)

columns_to_drop = ['Prediction', 'Delta', 'Comment', 'forecast_text', 'actual_date', 'forecast_day']
df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)

df['month'] = df['Date'].dt.month
df['week_of_year'] = df['Date'].dt.isocalendar().week
if 'holiday_flag' in df.columns:
    df['is_holiday_weekend'] = df['is_weekend'] * df['holiday_flag']
if 'rainfall' in df.columns and 'wind_speed' in df.columns:
    df['rain_and_wind'] = df['rainfall'] * df['wind_speed']

df = df.sort_values('Date')
df['wait_time_lag_1'] = df['Actual'].shift(1)
df['wait_time_roll_mean_3'] = df['Actual'].rolling(window=3).mean()
df['wait_time_roll_std_5'] = df['Actual'].rolling(window=5).mean()
df['wait_time_roll_std_7'] = df['Actual'].rolling(window=7).std()
df.fillna(0, inplace=True)

target = 'Actual'
eval_df = df[df['Date'] >= '2017-01-01'].copy()
X_eval = eval_df.drop(columns=['Date', target])
y_eval = eval_df[target]

X_eval['forecast_summary'] = X_eval['forecast_summary'].fillna("missing").astype(str)

numeric_features = X_eval.drop(columns=['forecast_summary']).select_dtypes(include=[np.number]).columns.tolist()

tfidf_vectorizer = joblib.load('../models/tfidf_vectorizer.pkl')
categorical_transformer = Pipeline(steps=[('tfidf', tfidf_vectorizer)])

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, 'forecast_summary')
    ]
)

X_eval_processed = preprocessor.fit_transform(X_eval)

model = joblib.load("../models/Gradient_Boosting_Base.pkl")

y_pred = model.predict(X_eval_processed)
rmse = sqrt(mean_squared_error(y_eval, y_pred))
r2 = r2_score(y_eval, y_pred)

#  Save Evaluation Metrics 
os.makedirs("../evaluation_metrics", exist_ok=True)
metrics_df = pd.DataFrame({
    "Metric": ["RMSE", "R2"],
    "Value": [rmse, r2]
})
metrics_df.to_csv("../evaluation_metrics/gradient_boosting_metrics_2017_2025.csv", index=False)

# Save Predictions vs Actuals 
pred_vs_actual = pd.DataFrame({
    "Actual": y_eval,
    "Predicted": y_pred
})
pred_vs_actual.to_csv("../evaluation_metrics/predictions_vs_actuals_2017_2025.csv", index=False)

#  Distribution Plot 
plt.figure(figsize=(8, 5))
plt.hist(y_eval, bins=30, alpha=0.5, label='Actual')
plt.hist(y_pred, bins=30, alpha=0.5, label='Predicted')
plt.title("Distribution (2017–2025): Actual vs Predicted Wait Times")
plt.legend()
plt.tight_layout()
plt.savefig("../evaluation_metrics/distribution_plot_2017_2025.png")
plt.close()

# Feature Importances 
if hasattr(model, "feature_importances_"):
    feature_names = numeric_features + [f"tfidf_{i}" for i in range(30)]
    importances = pd.DataFrame({
        "Feature": feature_names,
        "Importance": model.feature_importances_
    }).sort_values(by="Importance", ascending=False)

    importances.to_csv("../evaluation_metrics/feature_importance_2017_2025.csv", index=False)

    # Plot top 15
    top_n = 15
    top_features = importances.head(top_n)

    plt.figure(figsize=(10, 6))
    plt.barh(top_features["Feature"][::-1], top_features["Importance"][::-1])
    plt.title(f"Top {top_n} Most Important Features (2017–2025)")
    plt.xlabel("Importance")
    plt.tight_layout()
    plt.savefig("../evaluation_metrics/top_features_plot_2017_2025.png")
    plt.close()

# Save All Feature Importances 
if hasattr(model, "feature_importances_"):
    feature_names = numeric_features + [f"tfidf_{i}" for i in range(30)]
    importances = pd.DataFrame({
        "Feature": feature_names,
        "Importance": model.feature_importances_
    }).sort_values(by="Importance", ascending=False)

    # Save full feature importances to CSV
    full_importance_path = "../evaluation_metrics/full_feature_importance_2017_2025.csv"
    importances.to_csv(full_importance_path, index=False)
    print(f"\n📁 All feature importances saved to {full_importance_path}\n")

    print(importances.to_string(index=False))

plt.figure(figsize=(8, 6))

# Scatterplot with jitter using seaborn
sns.regplot(
    x=y_eval,
    y=y_pred,
    scatter_kws={'alpha': 0.5, 'edgecolor': 'k'},
    line_kws={'color': 'red', 'linestyle': '--'},
    x_jitter=0.8,
    y_jitter=0.8,
    fit_reg=False  # disables automatic regression line
)

# Manually plot diagonal line representing perfect predictions
plt.plot(
    [y_eval.min(), y_eval.max()],
    [y_eval.min(), y_eval.max()],
    'r--', lw=2
)

plt.xlabel("Actual Wait Time (min)")
plt.ylabel("Predicted Wait Time (min)")
plt.title(f"Actual vs Predicted (2017–2025)\nRMSE={rmse:.2f}, R²={r2:.3f}")

plt.tight_layout()
plt.savefig("../evaluation_metrics/scatterplot_actual_vs_predicted_2017_2025.png")
plt.close()

