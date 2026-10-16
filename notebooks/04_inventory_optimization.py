import pandas as pd

# Load inventory data
inventory = pd.read_csv(
    "data/raw/inventory_snapshots.csv",
    sep="\t"
)

# Load sales data
sales = pd.read_csv(
    "data/raw/sales_daily.csv"
)

# Load product master
sku_master = pd.read_csv(
    "data/raw/sku_master.csv"
)

print("Inventory Data Loaded")
print("Inventory Shape:", inventory.shape)
print("Sales Shape:", sales.shape)
print("SKU Master Shape:", sku_master.shape)

print("\nInventory Columns:")
print(inventory.columns.tolist())

print("\nFirst 5 Inventory Rows:")
print(inventory.head())

print("\nMissing Values:")
print(inventory.isnull().sum())
# Convert snapshot date to datetime
inventory["Snapshot_Date"] = pd.to_datetime(
    inventory["Snapshot_Date"],
    dayfirst=True
)

# Get the latest inventory snapshot for each SKU
latest_inventory = (
    inventory.sort_values("Snapshot_Date")
    .groupby("SKU")
    .tail(1)
    .sort_values("SKU")
    .reset_index(drop=True)
)

print("\nLatest Inventory Date:")
print(latest_inventory["Snapshot_Date"].max())

print("\nLatest Inventory Shape:", latest_inventory.shape)

print("\nLatest Stock for First 10 SKUs:")
print(
    latest_inventory[
        ["SKU", "Current_Stock", "On_Order",
         "Safety_Stock", "Reorder_Point"]
    ].head(10)
)
# Keep only SKUs available in sales and SKU master
common_skus = (
    set(sales["SKU"].astype(str).str.strip())
    & set(sku_master["SKU"].astype(str).str.strip())
    & set(latest_inventory["SKU"].astype(str).str.strip())
)

inventory_50 = latest_inventory[
    latest_inventory["SKU"].astype(str).str.strip().isin(common_skus)
].copy()

print("\nMatching Inventory SKUs:", inventory_50["SKU"].nunique())
print("Filtered Inventory Shape:", inventory_50.shape)

print("\nFiltered Inventory Preview:")
print(inventory_50[["SKU", "Current_Stock", "On_Order", "Reorder_Point"]].head(10))
# Calculate average daily demand for each SKU

sales["Date"] = pd.to_datetime(sales["Date"])

daily_demand = (
    sales.groupby("SKU")["Units_Sold"]
    .mean()
    .reset_index()
)

daily_demand.rename(
    columns={"Units_Sold": "Avg_Daily_Demand"},
    inplace=True
)

print("\nAverage Daily Demand:")
print(daily_demand.head(10))
# Merge inventory with average daily demand

inventory_analysis = inventory_50.merge(
    daily_demand,
    on="SKU",
    how="left"
)

# Add product details
inventory_analysis = inventory_analysis.merge(
    sku_master,
    on="SKU",
    how="left"
)

print("\nInventory Analysis Shape:", inventory_analysis.shape)

print("\nInventory Analysis Preview:")
print(
    inventory_analysis[
        ["SKU", "Current_Stock", "On_Order",
         "Avg_Daily_Demand", "Reorder_Point"]
    ].head(10)
)

print("\nMissing Values After Merge:")
print(inventory_analysis.isnull().sum())
# Load Aman's 30-day forecast

forecast = pd.read_csv(
    "data/processed/forecast_30_days.csv"
)

forecast["Date"] = pd.to_datetime(forecast["Date"])

print("\nForecast Shape:", forecast.shape)

print("\nForecast Columns:")
print(forecast.columns.tolist())

print("\nForecast Summary:")
print("Total Forecasted Demand:",
      round(forecast["Forecasted_Units_Sold"].sum(), 2))

print("Average Daily Forecast:",
      round(forecast["Forecasted_Units_Sold"].mean(), 2))
# Estimate SKU-wise demand using historical sales share

total_historical_sales = sales["Units_Sold"].sum()

sku_sales = (
    sales.groupby("SKU")["Units_Sold"]
    .sum()
    .reset_index()
)

sku_sales["Sales_Share"] = (
    sku_sales["Units_Sold"] / total_historical_sales
)

total_forecast = forecast["Forecasted_Units_Sold"].sum()

sku_sales["Forecast_30_Days"] = (
    sku_sales["Sales_Share"] * total_forecast
)

inventory_analysis = inventory_analysis.merge(
    sku_sales[["SKU", "Sales_Share", "Forecast_30_Days"]],
    on="SKU",
    how="left"
)

print("\nSKU-wise Estimated 30-Day Demand:")
print(
    inventory_analysis[
        ["SKU", "Avg_Daily_Demand", "Sales_Share",
         "Forecast_30_Days"]
    ].head(10)
)

print(
    "\nTotal Allocated Forecast:",
    round(inventory_analysis["Forecast_30_Days"].sum(), 2)
)
# Calculate inventory risk and reorder quantity

inventory_analysis["Available_Stock"] = (
    inventory_analysis["Current_Stock"]
    + inventory_analysis["On_Order"]
)

inventory_analysis["Lead_Time_Demand"] = (
    inventory_analysis["Avg_Daily_Demand"]
    * inventory_analysis["Lead_Time_Days"]
)

inventory_analysis["Stockout_Risk"] = (
    inventory_analysis["Available_Stock"]
    < inventory_analysis["Lead_Time_Demand"]
)

inventory_analysis["Overstock_Risk"] = (
    inventory_analysis["Current_Stock"]
    > inventory_analysis["Forecast_30_Days"] * 2
)

# Target stock: 30-day forecast + safety stock
inventory_analysis["Target_Stock"] = (
    inventory_analysis["Forecast_30_Days"]
    + inventory_analysis["Safety_Stock"]
)

# Recommended reorder quantity
inventory_analysis["Recommended_Reorder_Qty"] = (
    inventory_analysis["Target_Stock"]
    - inventory_analysis["Available_Stock"]
).clip(lower=0).round().astype(int)

print("\nInventory Risk Summary:")
print("Stockout Risk:", inventory_analysis["Stockout_Risk"].sum())
print("Overstock Risk:", inventory_analysis["Overstock_Risk"].sum())

print("\nReorder Recommendations:")
print(
    inventory_analysis[
        ["SKU", "Current_Stock", "On_Order",
         "Forecast_30_Days", "Stockout_Risk",
         "Overstock_Risk", "Recommended_Reorder_Qty"]
    ].head(10)
)
# Save inventory recommendations

import os

os.makedirs("data/processed", exist_ok=True)

inventory_analysis.to_csv(
    "data/processed/inventory_recommendations.csv",
    index=False
)

print("\nInventory recommendations saved successfully!")
print("File: data/processed/inventory_recommendations.csv")
print("Total SKUs:", len(inventory_analysis))
print(
    "SKUs needing reorder:",
    (inventory_analysis["Recommended_Reorder_Qty"] > 0).sum()
)
# Validate final inventory recommendations

print("\nFinal Validation")
print("Total SKUs:", len(inventory_analysis))
print("Duplicate SKUs:", inventory_analysis["SKU"].duplicated().sum())
print("Missing Values:", inventory_analysis.isnull().sum().sum())
print(
    "Total Reorder Quantity:",
    inventory_analysis["Recommended_Reorder_Qty"].sum()
)

print("\nTop 10 SKUs Needing Reorder:")
print(
    inventory_analysis.loc[
        inventory_analysis["Recommended_Reorder_Qty"] > 0,
        ["SKU", "Current_Stock", "On_Order",
         "Forecast_30_Days", "Recommended_Reorder_Qty"]
    ]
    .sort_values("Recommended_Reorder_Qty", ascending=False)
    .head(10)
)
import matplotlib.pyplot as plt

# Chart 1: Current Stock vs 30-Day Forecast
chart_data = inventory_analysis.head(10)

plt.figure(figsize=(12, 6))

plt.bar(
    chart_data["SKU"],
    chart_data["Current_Stock"],
    label="Current Stock"
)

plt.bar(
    chart_data["SKU"],
    chart_data["Forecast_30_Days"],
    alpha=0.7,
    label="Estimated 30-Day Demand"
)

plt.title("Current Stock vs Estimated 30-Day Demand")
plt.xlabel("SKU")
plt.ylabel("Units")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("data/processed/inventory_stock_vs_demand.png")
plt.show()


# Chart 2: Top 10 Reorder Recommendations
top_reorder = (
    inventory_analysis[
        inventory_analysis["Recommended_Reorder_Qty"] > 0
    ]
    .nlargest(10, "Recommended_Reorder_Qty")
)

plt.figure(figsize=(12, 6))

plt.bar(
    top_reorder["SKU"],
    top_reorder["Recommended_Reorder_Qty"]
)

plt.title("Top 10 Reorder Recommendations")
plt.xlabel("SKU")
plt.ylabel("Recommended Reorder Quantity")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("data/processed/top_10_reorder_recommendations.png")
plt.show()

print("Inventory charts saved successfully!")