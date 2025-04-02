import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
from math import sqrt
from sklearn.feature_extraction.text import TfidfVectorizer
import seaborn as sns

## Testing this on real world labelled data from 2022 28 Dec to 2025.

# === Load Dataset ===
attendance_df = pd.read_csv("../../../data/singapore_tourism_data/Final/synthetic_data_daily_attendance/synthetic_daily_attendance_2017_2025.csv")
weather_df = pd.read_csv("../../../data/Meteorological/datasets/final_data/merged_weather_data_clean.csv")
school_holidays_df = pd.read_csv("../../../data/Events/Holidays/datasets/daily_school_holidays_combined_updated.csv")
events_df = pd.read_csv("../../../data/Events/EventData/supplementary_event_data_2016_2025.csv")

attendance_df['Date'] = pd.to_datetime(attendance_df['Date'])
weather_df['date'] = pd.to_datetime(weather_df['date'], format='%d/%m/%Y')
school_holidays_df['date'] = pd.to_datetime(school_holidays_df['date'], format='%d/%m/%Y')
events_df['Date'] = pd.to_datetime(events_df['Date'], dayfirst=True, errors='coerce')
events_df = events_df.dropna(subset=['Date'])

df = attendance_df.copy()
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

columns_to_drop = ['forecast_text', 'actual_date', 'forecast_day']
df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)

df['month'] = df['Date'].dt.month
df['week_of_year'] = df['Date'].dt.isocalendar().week
if 'holiday_flag' in df.columns:
    df['is_holiday_weekend'] = df['is_weekend'] * df['holiday_flag']
if 'rainfall' in df.columns and 'wind_speed' in df.columns:
    df['rain_and_wind'] = df['rainfall'] * df['wind_speed']

df = df.sort_values('Date')
df['attdn_lag_1'] = df['USSAttendance'].shift(1)
df['attdn_roll_mean_3'] = df['USSAttendance'].rolling(window=3).mean()
df['attdn_roll_std_5'] = df['USSAttendance'].rolling(window=5).mean()
df['attdn_roll_std_7'] = df['USSAttendance'].rolling(window=7).std()
df.fillna(0, inplace=True)

# === Prepare evaluation data from 2022 28 December onward ===
target = 'USSAttendance'
eval_df = df.copy()
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

os.makedirs("../evaluation_metrics", exist_ok=True)
metrics_df = pd.DataFrame({
    "Metric": ["RMSE", "R2"],
    "Value": [rmse, r2]
})
metrics_df.to_csv("../evaluation_metrics/gradient_boosting_metrics_2017_2025.csv", index=False)

# Save Prediction vs Actual
pred_vs_actual = pd.DataFrame({
    "Actual": y_eval,
    "Predicted": y_pred
})
pred_vs_actual.to_csv("../evaluation_metrics/predictions_vs_actuals_2017_2025.csv", index=False)

#  Distribution Plot Histogram Chart
plt.figure(figsize=(8, 5))
plt.hist(y_eval, bins=30, alpha=0.5, label='Actual')
plt.hist(y_pred, bins=30, alpha=0.5, label='Predicted')
plt.title("Distribution 2017–2025 Actual vs Predicted Attendance")
plt.legend()
plt.tight_layout()
plt.savefig("../evaluation_metrics/distribution_plot_2017_2025.png")
plt.close()

# Feature Importances boxplot and csv generation
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

# Scatterplot of Actual vs Predicted for USS Attendance
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

plt.xlabel("Actual Daily Attendance")
plt.ylabel("Predicted Daily Attendance")
plt.title(f"Actual vs Predicted (2017–2025)\nRMSE={rmse:.2f}, R²={r2:.3f}")

plt.tight_layout()
plt.savefig("../evaluation_metrics/scatterplot_actual_vs_predicted_attdn_2017_2025.png")
plt.close()
