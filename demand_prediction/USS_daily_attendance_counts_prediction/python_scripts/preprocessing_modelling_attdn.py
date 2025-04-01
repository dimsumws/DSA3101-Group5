import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.feature_selection import VarianceThreshold
from sklearn.decomposition import PCA
from xgboost import XGBRegressor
from datetime import datetime
from math import sqrt
import seaborn as sns
import os
import joblib
from faker import Faker
import matplotlib.pyplot as plt

# Load, Merge, and Initial Preprocessing ===
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

columns_to_drop = ['Prediction', 'Delta', 'Comment', 'forecast_text', 'actual_date', 'forecast_day']
df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)

# Add time-based and interaction features
df['month'] = df['Date'].dt.month
df['week_of_year'] = df['Date'].dt.isocalendar().week
if 'holiday_flag' in df.columns:
    df['is_holiday_weekend'] = df['is_weekend'] * df['holiday_flag']
if 'rainfall' in df.columns and 'wind_speed' in df.columns:
    df['rain_and_wind'] = df['rainfall'] * df['wind_speed']

# Lag and rolling features, this would be good for 7 days basis
df = df.sort_values('Date')
df['attdn_lag_1'] = df['USSAttendance'].shift(1)
df['attdn_roll_mean_3'] = df['USSAttendance'].rolling(window=3).mean()
df['attdn_roll_std_5'] = df['USSAttendance'].rolling(window=5).mean()
df['attdn_roll_std_7'] = df['USSAttendance'].rolling(window=7).std()
df.fillna(0, inplace=True)

# Redefine target and features
target = 'USSAttendance'
X = df.drop(columns=['Date', target])
y = df[target]

X['forecast_summary'] = X['forecast_summary'].fillna("missing").astype(str)

categorical_transformer = Pipeline(steps=[
    ('tfidf', TfidfVectorizer(max_features=30))
])

numeric_features = X.drop(columns=['forecast_summary']).select_dtypes(include=[np.number]).columns.tolist()
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

X_processed = preprocessor.fit_transform(X)

tfidf_vectorizer = preprocessor.named_transformers_['cat'].named_steps['tfidf']
joblib.dump(tfidf_vectorizer, '../models/tfidf_vectorizer.pkl')

X_train, X_test, y_train, y_test = train_test_split(
    X_processed, y, test_size=0.2, random_state=42
)

# Apply Variance Threshold
selector = VarianceThreshold(threshold=0.01)
X_train_vt = selector.fit_transform(X_train)
X_test_vt = selector.transform(X_test)

# Apply PCA 
pca = PCA(n_components=0.95, random_state=42)  # Retain 95% variance
X_train_pca = pca.fit_transform(X_train)
X_test_pca = pca.transform(X_test)

# Apply both Variance Threshold + PCA
X_train_vt_pca = pca.fit_transform(X_train_vt)
X_test_vt_pca = pca.transform(X_test_vt)

model_params = {
    'Linear Regression': {
        'model': LinearRegression(),
        'params': {}
    },
    'Ridge Regression': {
        'model': Ridge(),
        'params': {'alpha': [0.1, 1.0, 10.0]}
    },
    'Lasso Regression': {
        'model': Lasso(),
        'params': {'alpha': [0.01, 0.1, 1.0]}
    },
    'Support Vector Regression': {
        'model': SVR(),
        'params': {'C': [0.1, 1, 10], 'epsilon': [0.1, 0.2, 0.5]}
    },
    'Gradient Boosting': {
        'model': GradientBoostingRegressor(random_state=42),
        'params': {'n_estimators': [100, 200], 'learning_rate': [0.05, 0.1], 'max_depth': [3, 5]}
    },
    'Random Forest': {
        'model': RandomForestRegressor(random_state=42),
        'params': {'n_estimators': [100, 200], 'max_depth': [10, 20], 'min_samples_split': [2, 5]}
    },
    'XGBoost': {
        'model': XGBRegressor(random_state=42, verbosity=0),
        'params': {'n_estimators': [100, 200], 'learning_rate': [0.05, 0.1], 'max_depth': [3, 5]}
    }
}

scenarios = {
    'Base': (X_train, X_test),
    'VarianceThreshold': (X_train_vt, X_test_vt),
    'PCA': (X_train_pca, X_test_pca),
    'VarianceThreshold+PCA': (X_train_vt_pca, X_test_vt_pca)
}

final_results = {}

for scenario_name, (train_set, test_set) in scenarios.items():
    print(f"\n=== Scenario: {scenario_name} ===")
    for name, mp in model_params.items():
        print(f"Tuning {name}...")
        if mp['params']:
            search = RandomizedSearchCV(mp['model'], mp['params'], n_iter=5, cv=3, scoring='neg_mean_squared_error', random_state=42, n_jobs=-1)
            search.fit(train_set, y_train)
            model = search.best_estimator_
            best_params = search.best_params_
        else:
            model = mp['model']
            model.fit(train_set, y_train)
            best_params = 'Default'

        y_train_pred = model.predict(train_set)
        y_test_pred = model.predict(test_set)

        train_rmse = sqrt(mean_squared_error(y_train, y_train_pred))
        test_rmse = sqrt(mean_squared_error(y_test, y_test_pred))
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)

        final_results[f"{name} ({scenario_name})"] = {
            'Train RMSE': train_rmse,
            'Train R2': train_r2,
            'Test RMSE': test_rmse,
            'Test R2': test_r2,
            'Best Params': best_params
        }

for model_scenario, metrics in final_results.items():
    print(f"{model_scenario}:")
    print(f" Train RMSE: {metrics['Train RMSE']:.2f}")
    print(f" Train R²:   {metrics['Train R2']:.3f}")
    print(f" Test RMSE:  {metrics['Test RMSE']:.2f}")
    print(f" Test R²:    {metrics['Test R2']:.3f}")
    print(f" Best Parameters: {metrics['Best Params']}\n")

os.makedirs("../models", exist_ok=True)
model_store = {}

for scenario_name, (train_set, test_set) in scenarios.items():
    for name, mp in model_params.items():
        key = f"{name} ({scenario_name})"
        model_path = f"../models/{key.replace(' ', '_').replace('(', '').replace(')', '')}.pkl"
        if mp['params']:
            search = RandomizedSearchCV(mp['model'], mp['params'], n_iter=1, cv=3, scoring='neg_mean_squared_error', random_state=42, n_jobs=-1)
            search.fit(train_set, y_train)
            model = search.best_estimator_
        else:
            model = mp['model']
            model.fit(train_set, y_train)

        joblib.dump(model, model_path)
        model_store[key] = model

best_model_key = "Gradient Boosting (Base)"
best_model = model_store[best_model_key]
y_pred = best_model.predict(X_test)
y_eval = y_test  # actual values
rmse = sqrt(mean_squared_error(y_eval, y_pred))
r2 = r2_score(y_eval, y_pred)
os.makedirs("../evaluation_metrics", exist_ok=True)

# Histogram Distribution Plot 
plt.figure(figsize=(8, 5))
plt.hist(y_eval, bins=30, alpha=0.5, label='Actual')
plt.hist(y_pred, bins=30, alpha=0.5, label='Predicted')
plt.title("Distribution 2017–2025 Actual vs Predicted Attendance")
plt.xlabel("Attendance")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.savefig("../evaluation_metrics/distribution_plot_2017_2025.png")
plt.close()

# Scatterplot of Actual vs Predicted
plt.figure(figsize=(8, 6))

# Scatterplot with jitter 
sns.regplot(
    x=y_eval,
    y=y_pred,
    scatter_kws={'alpha': 0.5, 'edgecolor': 'k'},
    line_kws={'color': 'red', 'linestyle': '--'},
    x_jitter=0.8,
    y_jitter=0.8,
    fit_reg=False
)

# Diagonal line for best fit line
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

# Feature importance (coefficients)
if hasattr(best_model, "coef_"):
    numeric_feature_names = numeric_features
    tfidf_feature_names = [f"tfidf_{i}" for i in range(30)]
    feature_names = numeric_feature_names + tfidf_feature_names

    importances = pd.DataFrame({
        "Feature": feature_names,
        "Importance": best_model.coef_
    }).sort_values(by="Importance", key=lambda x: np.abs(x), ascending=False)

    full_importance_path = "../evaluation_metrics/feature_importance_linear_regression_2017_2025.csv"
    importances.to_csv(full_importance_path, index=False)
    print(importances.to_string(index=False))
    top_n = 10
    top_features = importances.head(top_n)

    plt.figure(figsize=(10, 6))
    plt.barh(top_features["Feature"][::-1], top_features["Importance"][::-1])
    plt.title(f"Top {top_n} Most Important Features (Linear Regression, 2017–2025)")
    plt.xlabel("Coefficient Importance")
    plt.tight_layout()
    plt.savefig("../evaluation_metrics/top_features_linear_regression_2017_2025.png")
    plt.close()