import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load prepared forecasting data
data = pd.read_csv("data/processed/forecasting_data.csv")

# Convert Date to datetime
data["Date"] = pd.to_datetime(data["Date"])

print("Forecasting Data Loaded")
print("Shape:", data.shape)
print("\nDate Range:")
print(data["Date"].min(), "to", data["Date"].max())

print("\nColumns:")
print(data.columns.tolist())

# Prepare daily demand
daily_demand = (
    data.groupby("Date")["Units_Sold"]
    .sum()
    .reset_index()
)

print("\nDaily Demand:")
print(daily_demand.head(10))

print("\nDaily Demand Shape:")
print(daily_demand.shape)

print("\nDaily Demand Statistics:")
print(daily_demand["Units_Sold"].describe())
# Train-Test Split
train_size = int(len(daily_demand) * 0.8)

train = daily_demand.iloc[:train_size].copy()
test = daily_demand.iloc[train_size:].copy()

print("\nTrain Data:")
print(train.shape)
print(train["Date"].min(), "to", train["Date"].max())

print("\nTest Data:")
print(test.shape)
print(test["Date"].min(), "to", test["Date"].max())
# Prepare data for forecasting model
X_train = np.arange(len(train)).reshape(-1, 1)
y_train = train["Units_Sold"].values

X_test = np.arange(len(train), len(train) + len(test)).reshape(-1, 1)
y_test = test["Units_Sold"].values

print("\nModel Data Ready")
print("X_train:", X_train.shape)
print("X_test:", X_test.shape)
from sklearn.linear_model import LinearRegression

# Create and train forecasting model
model = LinearRegression()

model.fit(X_train, y_train)

# Predict test data
test_predictions = model.predict(X_test)

print("\nModel trained successfully!")
print("First 10 predictions:")
print(test_predictions[:10])
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Calculate evaluation metrics
mae = mean_absolute_error(y_test, test_predictions)
rmse = np.sqrt(mean_squared_error(y_test, test_predictions))
mape = np.mean(
    np.abs((y_test - test_predictions) / y_test)
) * 100

print("\nModel Evaluation:")
print("MAE:", round(mae, 2))
print("RMSE:", round(rmse, 2))
print("MAPE:", round(mape, 2), "%")
# Create time-series lag features
forecast_data = daily_demand.copy()

forecast_data["lag_1"] = forecast_data["Units_Sold"].shift(1)
forecast_data["lag_7"] = forecast_data["Units_Sold"].shift(7)
forecast_data["lag_14"] = forecast_data["Units_Sold"].shift(14)
forecast_data["lag_30"] = forecast_data["Units_Sold"].shift(30)

# Rolling demand features
forecast_data["rolling_7"] = (
    forecast_data["Units_Sold"].shift(1).rolling(7).mean()
)

forecast_data["rolling_30"] = (
    forecast_data["Units_Sold"].shift(1).rolling(30).mean()
)

# Remove rows created by lagging
forecast_data = forecast_data.dropna().reset_index(drop=True)

print("\nTime-Series Features Created")
print(forecast_data.head())
print("\nShape:", forecast_data.shape)
from sklearn.ensemble import RandomForestRegressor

# Features and target
features = [
    "lag_1",
    "lag_7",
    "lag_14",
    "lag_30",
    "rolling_7",
    "rolling_30"
]

X = forecast_data[features]
y = forecast_data["Units_Sold"]

# Time-based train/test split
split = int(len(forecast_data) * 0.8)

X_train_ts = X.iloc[:split]
X_test_ts = X.iloc[split:]

y_train_ts = y.iloc[:split]
y_test_ts = y.iloc[split:]

# Train Random Forest model
rf_model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

rf_model.fit(X_train_ts, y_train_ts)

# Predictions
rf_predictions = rf_model.predict(X_test_ts)

print("\nRandom Forest Model trained successfully!")
print("Training rows:", len(X_train_ts))
print("Testing rows:", len(X_test_ts))

# Evaluate Random Forest model

rf_mae = mean_absolute_error(y_test_ts, rf_predictions)
rf_rmse = np.sqrt(mean_squared_error(y_test_ts, rf_predictions))
rf_mape = np.mean(
    np.abs((y_test_ts - rf_predictions) / y_test_ts)
) * 100

print("\nRandom Forest Evaluation:")
print("MAE:", round(rf_mae, 2))
print("RMSE:", round(rf_rmse, 2))
print("MAPE:", round(rf_mape, 2), "%")
# Actual vs Predicted Demand

plt.figure(figsize=(12, 5))

plt.plot(
    y_test,
    label="Actual Demand"
)

plt.plot(
    rf_predictions,
    label="Predicted Demand"
)

plt.title("Actual vs Predicted Demand - Random Forest")
plt.xlabel("Test Data Points")
plt.ylabel("Units Sold")
plt.legend()
plt.tight_layout()
plt.show()
# Trend and Seasonality Analysis

# 7-Day Rolling Trend
daily_demand["rolling_7"] = (
    daily_demand["Units_Sold"].rolling(7).mean()
)

plt.figure(figsize=(12, 5))

plt.plot(
    daily_demand["Date"],
    daily_demand["Units_Sold"],
    label="Daily Demand"
)

plt.plot(
    daily_demand["Date"],
    daily_demand["rolling_7"],
    label="7-Day Trend"
)

plt.title("Demand Trend Analysis")
plt.xlabel("Date")
plt.ylabel("Units Sold")
plt.legend()
plt.tight_layout()
plt.show()


# Weekday Seasonality
daily_demand["Day_of_Week"] = (
    daily_demand["Date"].dt.day_name()
)

weekday_demand = (
    daily_demand.groupby("Day_of_Week")["Units_Sold"]
    .mean()
    .reindex([
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ])
)

print("\nAverage Demand by Weekday:")
print(weekday_demand)


plt.figure(figsize=(10, 5))

plt.bar(
    weekday_demand.index,
    weekday_demand.values
)

plt.title("Weekly Seasonality - Average Demand")
plt.xlabel("Day of Week")
plt.ylabel("Average Units Sold")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
# 30-Day Demand Forecast

forecast_history = daily_demand["Units_Sold"].tolist()

future_predictions = []

for i in range(30):

    lag_1 = forecast_history[-1]
    lag_7 = forecast_history[-7]
    lag_14 = forecast_history[-14]
    lag_30 = forecast_history[-30]

    rolling_7 = np.mean(forecast_history[-7:])
    rolling_30 = np.mean(forecast_history[-30:])

    future_features = pd.DataFrame([[
        lag_1,
        lag_7,
        lag_14,
        lag_30,
        rolling_7,
        rolling_30
    ]], columns=features)

    prediction = rf_model.predict(future_features)[0]

    future_predictions.append(prediction)
    forecast_history.append(prediction)


future_dates = pd.date_range(
    start=daily_demand["Date"].max() + pd.Timedelta(days=1),
    periods=30,
    freq="D"
)

forecast_30_days = pd.DataFrame({
    "Date": future_dates,
    "Forecasted_Units_Sold": future_predictions
})

print("\n30-Day Demand Forecast:")
print(forecast_30_days)

print("\n30-Day Forecast Summary:")
print("Total Forecasted Demand:",
      round(forecast_30_days["Forecasted_Units_Sold"].sum(), 2))

print("Average Daily Forecast:",
      round(forecast_30_days["Forecasted_Units_Sold"].mean(), 2))
# Save 30-Day Forecast
forecast_30_days.to_csv(
    "data/processed/forecast_30_days.csv",
    index=False
)

print("\n30-Day Forecast saved successfully!")
# Save trained Random Forest model

import joblib

joblib.dump(
    rf_model,
    "data/processed/random_forest_demand_model.pkl"
)

print("Random Forest model saved successfully!")