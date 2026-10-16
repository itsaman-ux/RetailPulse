import pandas as pd

# Load sales data
sales = pd.read_csv("data/raw/sales_daily.csv")

# Convert Date column to datetime
sales["Date"] = pd.to_datetime(sales["Date"], errors="coerce")

# Basic validation
print("Invalid Dates:", sales["Date"].isna().sum())
print("Start Date:", sales["Date"].min())
print("End Date:", sales["Date"].max())
print("Negative Units Sold:", (sales["Units_Sold"] < 0).sum())
print("Negative Revenue:", (sales["Revenue"] < 0).sum())
print("Duplicate Rows:", sales.duplicated().sum())

print("\nData Types:")
print(sales.dtypes)

# SKU-wise time-series check
print("\nNumber of SKUs:", sales["SKU"].nunique())

print("\nSales records per SKU:")
print(sales.groupby("SKU")["Date"].nunique().describe())

print("\nDate coverage per SKU:")
sku_dates = sales.groupby("SKU")["Date"].agg(["min", "max", "nunique"])
print(sku_dates.head(10))