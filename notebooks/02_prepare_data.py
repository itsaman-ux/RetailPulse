import pandas as pd

# Load official datasets
sales = pd.read_csv("data/raw/sales_daily.csv")
sku = pd.read_csv("data/raw/sku_master.csv")
calendar = pd.read_csv("data/raw/calendar.csv")

# Convert date columns
sales["Date"] = pd.to_datetime(sales["Date"])
calendar["date"] = pd.to_datetime(calendar["date"])

# Basic information
print("SALES DATA:", sales.shape)
print("SKU MASTER:", sku.shape)
print("CALENDAR:", calendar.shape)

print("\nSales columns:")
print(sales.columns.tolist())

print("\nSKU columns:")
print(sku.columns.tolist())

print("\nCalendar columns:")
print(calendar.columns.tolist())

print("\nSales date range:")
print(sales["Date"].min(), "to", sales["Date"].max())

print("\nCalendar date range:")
print(calendar["date"].min(), "to", calendar["date"].max())
# Check SKU matching
sales_skus = set(sales["SKU"].unique())
master_skus = set(sku["SKU"].unique())

missing_in_master = sales_skus - master_skus
unused_in_sales = master_skus - sales_skus

print("\nSKU Matching Check")
print("SKUs in sales:", len(sales_skus))
print("SKUs in master:", len(master_skus))
print("Sales SKUs missing from master:", len(missing_in_master))
print("Master SKUs not present in sales:", len(unused_in_sales))

if missing_in_master:
    print("Missing SKUs:", sorted(missing_in_master))

    # Merge sales data with SKU master
sales_sku = sales.merge(
    sku,
    on="SKU",
    how="left"
)

print("\nAfter Sales + SKU Master Merge:")
print("Shape:", sales_sku.shape)

print("\nMissing Product Information:")
print(sales_sku["Product_Name"].isna().sum())

print("\nMerged Data Sample:")
print(sales_sku.head())
# Merge calendar data
final_data = sales_sku.merge(
    calendar,
    left_on="Date",
    right_on="date",
    how="left"
)

print("\nAfter Calendar Merge:")
print("Shape:", final_data.shape)

print("\nMissing Calendar Information:")
print(final_data["year"].isna().sum())

print("\nFinal Data Sample:")
print(final_data.head())

# Trend analysis: monthly demand
monthly_demand = (
    final_data
    .groupby(final_data["Date"].dt.to_period("M"))["Units_Sold"]
    .sum()
    .reset_index()
)

monthly_demand["Date"] = monthly_demand["Date"].dt.to_timestamp()

print("\nMonthly Demand:")
print(monthly_demand)

# Year-wise demand
yearly_demand = (
    final_data
    .groupby(final_data["Date"].dt.year)["Units_Sold"]
    .sum()
)

print("\nYear-wise Demand:")
print(yearly_demand)
# Seasonality analysis

# Monthly seasonality
monthly_pattern = (
    final_data
    .groupby(final_data["Date"].dt.month)["Units_Sold"]
    .mean()
)

print("\nAverage Demand by Month:")
print(monthly_pattern)

# Weekday seasonality
weekday_pattern = (
    final_data
    .groupby("day_of_week")["Units_Sold"]
    .mean()
)

print("\nAverage Demand by Weekday:")
print(weekday_pattern)

# Seasonal pattern
season_pattern = (
    final_data
    .groupby("season")["Units_Sold"]
    .mean()
)

print("\nAverage Demand by Season:")
print(season_pattern)

import matplotlib.pyplot as plt

# Monthly demand trend
plt.figure(figsize=(12, 5))
plt.plot(monthly_demand["Date"], monthly_demand["Units_Sold"])
plt.title("Monthly Demand Trend")
plt.xlabel("Date")
plt.ylabel("Units Sold")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Seasonal demand
season_order = ["Spring", "Summer", "Monsoon", "Autumn", "Winter"]

season_plot = (
    final_data.groupby("season")["Units_Sold"]
    .mean()
    .reindex(season_order)
)

plt.figure(figsize=(8, 5))
plt.bar(season_plot.index, season_plot.values)
plt.title("Average Demand by Season")
plt.xlabel("Season")
plt.ylabel("Average Units Sold")
plt.tight_layout()
plt.show()

# Save forecasting-ready dataset
output_path = "data/processed/forecasting_data.csv"

final_data.to_csv(output_path, index=False)

print("\nForecasting dataset saved successfully!")
print("File:", output_path)
print("Shape:", final_data.shape)