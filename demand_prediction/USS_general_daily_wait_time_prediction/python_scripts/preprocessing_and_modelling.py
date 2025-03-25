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
import os
import joblib
from faker import Faker
import matplotlib.pyplot as plt

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

# Add time-based and interaction features
df['month'] = df['Date'].dt.month
df['week_of_year'] = df['Date'].dt.isocalendar().week
if 'holiday_flag' in df.columns:
    df['is_holiday_weekend'] = df['is_weekend'] * df['holiday_flag']
if 'rainfall' in df.columns and 'wind_speed' in df.columns:
    df['rain_and_wind'] = df['rainfall'] * df['wind_speed']

# Lag and rolling features (requires sorting), this would be good for 7 days basis
df = df.sort_values('Date')
df['wait_time_lag_1'] = df['Actual'].shift(1)
df['wait_time_roll_mean_3'] = df['Actual'].rolling(window=3).mean()
df['wait_time_roll_std_5'] = df['Actual'].rolling(window=5).mean()
df['wait_time_roll_std_7'] = df['Actual'].rolling(window=7).std()
df.fillna(0, inplace=True)

# Redefine target and features
target = 'Actual'
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

print("Final feature columns used for training (raw):")
print(X.columns.tolist())

tfidf_vectorizer = preprocessor.named_transformers_['cat'].named_steps['tfidf']
joblib.dump(tfidf_vectorizer, '../models/tfidf_vectorizer.pkl')
print("✅ Saved tfidf_vectorizer.pkl to ../models/")

# Print merged dataset shape and post-merge checks
print(f"Merged dataset shape: {df.shape}")
print(f"Processed feature shape: {X_processed.shape}")
X_train, X_test, y_train, y_test = train_test_split(
    X_processed, y, test_size=0.2, random_state=42
)

# Print train/test split shapes
print(f"X_train shape: {X_train.shape}, X_test shape: {X_test.shape}")
print(f"y_train shape: {y_train.shape}, y_test shape: {y_test.shape}")

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

# Define Models and Hyperparameter Grids 
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

# Train and Evaluate Models Across Preprocessing Scenarios 
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

# Print results
for model_scenario, metrics in final_results.items():
    print(f"{model_scenario}:")
    print(f"  Train RMSE: {metrics['Train RMSE']:.2f}")
    print(f"  Train R²:   {metrics['Train R2']:.3f}")
    print(f"  Test RMSE:  {metrics['Test RMSE']:.2f}")
    print(f"  Test R²:    {metrics['Test R2']:.3f}")
    print(f"  Best Params: {metrics['Best Params']}\n")

# Save All Optimized Models 
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
