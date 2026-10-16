
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="RetailPulse | Business Analyst",
    page_icon="📊",
    layout="wide"
)

# -------------------- LOAD DATA --------------------

@st.cache_data
def load_data():
    customers = pd.read_csv(
        "data/customer/processed/customer_analytics.csv"
    )
    churn = pd.read_csv(
        "data/customer/processed/churn_data.csv"
    )
    forecast = pd.read_csv(
        "data/processed/forecast_30_days.csv"
    )
    inventory = pd.read_csv(
        "data/processed/inventory_recommendations.csv"
    )
    return customers, churn, forecast, inventory


customers, churn, forecast, inventory = load_data()
forecast["Date"] = pd.to_datetime(forecast["Date"])
inventory["Stockout_Risk"] = inventory["Stockout_Risk"].astype(bool)

# -------------------- SIDEBAR --------------------

st.sidebar.title("📊 RetailPulse")

page = st.sidebar.selectbox(
    "Navigation",
    [
        "Executive Overview",
        "Customer Analytics",
        "Churn Analysis",
        "Demand Forecasting",
        "Inventory Optimization"
    ]
)

# -------------------- HEADER --------------------

st.title("📊 RetailPulse")
st.subheader("E-commerce Business Analyst Agent")
st.caption(
    "Customer insights • Churn analysis • Demand forecasting • Inventory planning"
)
st.divider()

# -------------------- EXECUTIVE OVERVIEW --------------------

if page == "Executive Overview":

    st.header("Executive Overview")
    st.write("A consolidated view of the RetailPulse analytics modules.")

    total_customers = len(customers)
    churned_customers = int((churn["Churn"] == 1).sum())
    churn_rate = (
        churned_customers / len(churn) * 100
        if len(churn) else 0
    )
    total_forecast = forecast["Forecasted_Units_Sold"].sum()
    reorder_skus = int(
        (inventory["Recommended_Reorder_Qty"] > 0).sum()
    )
    total_reorder = int(
        inventory["Recommended_Reorder_Qty"].sum()
    )
    stockout_skus = int(inventory["Stockout_Risk"].sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Customers Analyzed", f"{total_customers:,}")
    c2.metric("Churn Rate", f"{churn_rate:.2f}%")
    c3.metric("Customer Segments", str(customers["Segment"].nunique()))

    c4, c5, c6 = st.columns(3)
    c4.metric("30-Day Forecast", f"{total_forecast:,.0f} units")
    c5.metric("SKUs Needing Reorder", str(reorder_skus))
    c6.metric("Stockout Risk SKUs", str(stockout_skus))

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Customer Segments")
        st.bar_chart(customers["Segment"].value_counts())

    with right:
        st.subheader("30-Day Demand Forecast")
        st.line_chart(
            forecast.set_index("Date")["Forecasted_Units_Sold"]
        )

    st.subheader("Inventory Summary")
    st.write(f"**Total recommended reorder quantity:** {total_reorder:,} units")

    st.caption(
        "Note: Forecast covers the saved 30-day forecast period. "
        "Inventory figures use the latest available snapshot in the dataset."
    )

# -------------------- CUSTOMER ANALYTICS --------------------

elif page == "Customer Analytics":

    st.header("Customer Analytics")

    c1, c2 = st.columns(2)
    c1.metric("Total Customers", f"{len(customers):,}")
    c2.metric("Customer Segments", str(customers["Segment"].nunique()))

    st.subheader("Customer Segment Distribution")
    st.bar_chart(customers["Segment"].value_counts())

    st.subheader("Customer Data")
    st.dataframe(customers, use_container_width=True)

    st.download_button(
        "Download Customer Report",
        customers.to_csv(index=False),
        "customer_analytics.csv",
        "text/csv"
    )

# -------------------- CHURN ANALYSIS --------------------

elif page == "Churn Analysis":

    st.header("Churn Analysis")

    total = len(churn)
    churned = int((churn["Churn"] == 1).sum())
    non_churned = total - churned
    rate = churned / total * 100 if total else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Customers Analyzed", f"{total:,}")
    c2.metric("Churned Customers", f"{churned:,}")
    c3.metric("Churn Rate", f"{rate:.2f}%")

    st.subheader("Churn Distribution")
    distribution = pd.Series({
        "Churn": churned,
        "Non-Churn": non_churned
    })
    st.bar_chart(distribution)

    st.subheader("Churn Data")
    st.dataframe(churn, use_container_width=True)

    st.download_button(
        "Download Churn Report",
        churn.to_csv(index=False),
        "churn_data.csv",
        "text/csv"
    )

# -------------------- DEMAND FORECASTING --------------------

elif page == "Demand Forecasting":

    st.header("Demand Forecasting")

    c1, c2 = st.columns(2)
    c1.metric(
        "Total Forecasted Units",
        f"{forecast['Forecasted_Units_Sold'].sum():,.0f}"
    )
    c2.metric(
        "Average Daily Forecast",
        f"{forecast['Forecasted_Units_Sold'].mean():,.1f}"
    )

    st.subheader("30-Day Demand Forecast")
    st.line_chart(
        forecast.set_index("Date")["Forecasted_Units_Sold"]
    )

    st.subheader("Forecast Data")
    st.dataframe(forecast, use_container_width=True)

    st.download_button(
        "Download Forecast Report",
        forecast.to_csv(index=False),
        "forecast_30_days.csv",
        "text/csv"
    )

# -------------------- INVENTORY OPTIMIZATION --------------------

elif page == "Inventory Optimization":

    st.header("Inventory Optimization")

    reorder_skus = int(
        (inventory["Recommended_Reorder_Qty"] > 0).sum()
    )
    total_reorder = int(
        inventory["Recommended_Reorder_Qty"].sum()
    )
    stockout_skus = int(inventory["Stockout_Risk"].sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Total SKUs", f"{len(inventory):,}")
    c2.metric("SKUs Needing Reorder", f"{reorder_skus:,}")
    c3.metric("Total Recommended Reorder", f"{total_reorder:,} units")

    st.subheader("Stockout Risk")
    st.metric("SKUs at Stockout Risk", stockout_skus)

    st.subheader("Top 10 Reorder Recommendations")
    top_reorder = inventory.nlargest(
        10, "Recommended_Reorder_Qty"
    )
    st.bar_chart(
        top_reorder.set_index("SKU")["Recommended_Reorder_Qty"]
    )

    st.subheader("Inventory Recommendations")
    st.dataframe(
        inventory.sort_values(
            "Recommended_Reorder_Qty",
            ascending=False
        ),
        use_container_width=True
    )

    st.download_button(
        "Download Inventory Report",
        inventory.to_csv(index=False),
        "inventory_recommendations.csv",
        "text/csv"
    )
