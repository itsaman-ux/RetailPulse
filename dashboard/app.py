
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="RetailPulse | Retail Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- LANDING PAGE STATE ----------------
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False


ROOT = Path(__file__).resolve().parent.parent

# =========================================================
# THEME
# =========================================================
st.markdown("""
<style>
.stApp {
    background: #0b1020;
    color: #edf2ff;
}
.block-container {
    max-width: 1700px;
    padding: 1.5rem 2rem 2.5rem;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#151d35,#0e1426);
    border-right: 1px solid #293452;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1.4rem 1rem;
}
.hero {
    background: linear-gradient(120deg,#202b50,#31245a);
    border: 1px solid #414d77;
    padding: 26px 30px;
    border-radius: 18px;
    margin-bottom: 24px;
}
.hero h1 {
    color: white;
    font-size: 32px;
    margin: 0;
}
.hero p {
    color: #c4ccef;
    margin: 8px 0 0;
}
.kpi {
    background: linear-gradient(145deg,#18233d,#131a2e);
    border: 1px solid #303d60;
    border-radius: 15px;
    padding: 19px;
    min-height: 118px;
    margin-bottom: 8px;
}
.kpi-label {
    color: #aab8dc;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: .5px;
    margin-bottom: 13px;
}
.kpi-value {
    color: #fff;
    font-size: 28px;
    font-weight: 750;
}
.panel {
    background: #131b30;
    border: 1px solid #2a3655;
    border-radius: 14px;
    padding: 15px;
}
div[data-testid="stMetric"] {
    background: linear-gradient(145deg,#18233d,#131a2e);
    border: 1px solid #303d60;
    padding: 15px;
    border-radius: 13px;
}
[data-testid="stDataFrame"] {
    border: 1px solid #293754;
    border-radius: 10px;
}
.stButton button, .stDownloadButton button {
    border-radius: 9px;
}
.status-row {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #dbe5ff;
    font-size: 12px;
    padding: 8px 0;
    border-bottom: 1px solid rgba(90,110,150,.18);
}
.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    min-width: 8px;
    border-radius: 50%;
}
.status-dot.good { background: #34d399; box-shadow: 0 0 8px rgba(52,211,153,.35); }
.status-dot.bad { background: #fb7185; }
.status-state { margin-left: auto; font-size: 9px; letter-spacing: .5px; color: #9fb0d4; }
[data-testid="stPlotlyChart"] { border: 1px solid rgba(65,81,120,.35); border-radius: 12px; padding: 4px; }
h1, h2, h3 {
    letter-spacing: -.35px;
    color: #f4f7ff;
}
hr {
    border-color: #293452;
}
@media(max-width:768px) {
    .block-container {
        padding: 1rem;
    }
    .hero {
        padding: 20px;
    }
    .kpi-value {
        font-size: 23px;
    }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# DATA LOADING
# =========================================================
@st.cache_data
def load_csv(relative_path, separator=","):
    path = ROOT / relative_path
    if not path.exists():
        return None
    try:
        return pd.read_csv(path, sep=separator)
    except Exception:
        return None


customers = load_csv("data/customer/processed/customer_analytics.csv")
churn = load_csv("data/customer/processed/churn_data.csv")
forecast = load_csv("data/processed/forecast_30_days.csv")
inventory = load_csv("data/processed/inventory_recommendations.csv")

# =========================================================
# HELPERS
# =========================================================
def kpi(label, value, icon="📊"):
    st.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-label">{icon} &nbsp; {label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def missing_message(name):
    st.warning(
        f"{name} ka data file nahi mila. Project folder aur CSV path check karein."
    )


def download_csv(df, filename):
    st.download_button(
        "⬇️ Download CSV Report",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        use_container_width=False
    )


def prepare_plot(fig, height=380):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(9,14,27,0.7)",
        font=dict(color="#dce6ff", size=12),
        margin=dict(l=24, r=24, t=70, b=55),
        title=dict(x=0.02, xanchor="left", font=dict(size=16)),
        autosize=True,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            gridcolor="#273149",
            zeroline=False
        )
    )
    return fig


def metric_value(df, column, default=0):
    if df is None or column not in df.columns:
        return default
    return pd.to_numeric(df[column], errors="coerce").fillna(0)


def churn_flags(df):
    """Normalize numeric and common text churn labels."""
    if df is None or "Churn" not in df.columns:
        return pd.Series(dtype=bool)

    values = df["Churn"]
    numeric = pd.to_numeric(values, errors="coerce")

    if numeric.notna().all():
        return numeric.eq(1)

    text = values.astype(str).str.strip().str.lower()
    return text.isin(["1", "true", "yes", "churn", "churned"])


def stockout_flags(df):
    if df is None or "Stockout_Risk" not in df.columns:
        return pd.Series(dtype=bool)

    return (
        df["Stockout_Risk"]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes"])
    )


def section_title(title, subtitle=None):
    st.subheader(title)
    if subtitle:
        st.caption(subtitle)


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("# 📊 RetailPulse")
    st.caption("RETAIL INTELLIGENCE PLATFORM")
    st.divider()

    st.markdown("**WORKSPACE**")

    page = st.radio(
        "Navigate",
        [
            "Executive Overview",
            "Customer Analytics",
            "Churn Analysis",
            "Demand Forecasting",
            "Inventory Optimization"
        ],
        format_func=lambda x: {
            "Executive Overview": "🏠  Executive Overview",
            "Customer Analytics": "👥  Customer Analytics",
            "Churn Analysis": "🔍  Churn Analysis",
            "Demand Forecasting": "📈  Demand Forecasting",
            "Inventory Optimization": "📦  Inventory Optimization"
        }[x],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("**DATA STATUS**")
    data_status = [
        ("Customer analytics", customers),
        ("Churn analysis", churn),
        ("Demand forecast", forecast),
        ("Inventory recommendations", inventory),
    ]
    for module_name, module_df in data_status:
        if module_df is not None:
            st.markdown(f"<div class='status-row'><span class='status-dot good'></span>{module_name}<span class='status-state'>READY</span></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='status-row'><span class='status-dot bad'></span>{module_name}<span class='status-state'>MISSING</span></div>", unsafe_allow_html=True)

    st.divider()
    st.caption("RETAIL INTELLIGENCE SUITE")
    st.caption("Customer • Churn • Forecast • Inventory")


#
# ---------------- HOME PAGE ----------------
if not st.session_state.show_dashboard:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #10172f, #30215b, #493078);
        padding: 55px 35px;
        border-radius: 22px;
        border: 1px solid #4b5680;
        text-align: center;
        margin: 20px 0;
    ">
        <h1 style="font-size: 48px; color: white;">
            📊 RetailPulse
        </h1>
        <h3 style="color: #c4b5fd;">
            Retail Intelligence. Smarter Decisions.
        </h3>
        <p style="color: #e2e8f0; font-size: 17px;">
            Explore customer behavior, predict churn, forecast demand
            and optimize inventory — all in one platform.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Explore the Platform")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("### 👥")
        st.markdown("**Customer Analytics**")
        st.caption("Understand customer segments and value.")

    with c2:
        st.markdown("### 🔍")
        st.markdown("**Churn Intelligence**")
        st.caption("Explore customer churn patterns.")

    with c3:
        st.markdown("### 📈")
        st.markdown("**Demand Forecasting**")
        st.caption("Analyze the saved 30-day forecast.")

    with c4:
        st.markdown("### 📦")
        st.markdown("**Inventory Optimization**")
        st.caption("Review stock and reorder recommendations.")

    st.write("")
    left, center, right = st.columns([1, 2, 1])

    with center:
        if st.button("🚀  Launch RetailPulse Dashboard", use_container_width=True):
            st.session_state.show_dashboard = True
            st.rerun()

    st.stop()

# HEADER
# =========================================================
st.markdown("""
<div class="hero">
    <h1>📊 RetailPulse</h1>
    <p>AI-Powered Customer Analytics, Demand Forecasting
    &amp; Inventory Intelligence</p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# EXECUTIVE OVERVIEW
# =========================================================
if page == "Executive Overview":

    section_title(
        "Executive Overview",
        "A consolidated view of customer, churn, forecasting and inventory performance."
    )

    total_customers = len(customers) if customers is not None else 0

    churned = int(churn_flags(churn).sum()) if churn is not None else 0
    churn_rate = (
        churned / len(churn) * 100
        if churn is not None and len(churn) else 0
    )

    segments = (
        customers["Segment"].nunique()
        if customers is not None and "Segment" in customers.columns
        else 0
    )

    forecast_total = (
        metric_value(forecast, "Forecasted_Units_Sold").sum()
        if forecast is not None else 0
    )

    reorder_count = (
        int((metric_value(inventory, "Recommended_Reorder_Qty") > 0).sum())
        if inventory is not None else 0
    )

    stockout_count = (
        int(stockout_flags(inventory).sum())
        if inventory is not None else 0
    )

    # KPI ROW 1
    a, b, c = st.columns(3)

    with a:
        kpi("CUSTOMERS ANALYZED", f"{total_customers:,}", "👥")
    with b:
        kpi("CHURN RATE", f"{churn_rate:.2f}%", "🔍")
    with c:
        kpi("CUSTOMER SEGMENTS", f"{segments}", "🎯")

    # KPI ROW 2
    d, e, f = st.columns(3)

    with d:
        kpi("30-DAY FORECAST", f"{forecast_total:,.0f} units", "📈")
    with e:
        kpi("SKUs NEEDING REORDER", f"{reorder_count}", "📦")
    with f:
        kpi("STOCKOUT RISK SKUs", f"{stockout_count}", "⚠️")

    st.divider()

    # CUSTOMER AND FORECAST CHARTS
    left, right = st.columns(2)

    with left:
        section_title("👥 Customer Segment Distribution")

        if customers is not None and "Segment" in customers.columns:
            segment_counts = (
                customers["Segment"]
                .fillna("Unknown")
                .value_counts()
                .rename_axis("Customer Segment")
                .reset_index(name="Customers")
            )

            fig = px.bar(
                segment_counts,
                x="Customer Segment",
                y="Customers",
                color="Customer Segment",
                text="Customers",
                title="Customers by Segment"
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False)
            st.plotly_chart(
                prepare_plot(fig),
                use_container_width=True,
                key="overview_segments"
            )
        else:
            missing_message("Customer Analytics")

    with right:
        section_title("📈 30-Day Demand Forecast")

        if (
            forecast is not None
            and {"Date", "Forecasted_Units_Sold"}.issubset(forecast.columns)
        ):
            forecast_plot = forecast.copy()
            forecast_plot["Date"] = pd.to_datetime(
                forecast_plot["Date"], errors="coerce"
            )
            forecast_plot["Forecasted_Units_Sold"] = pd.to_numeric(
                forecast_plot["Forecasted_Units_Sold"], errors="coerce"
            )
            forecast_plot = forecast_plot.dropna(
                subset=["Date", "Forecasted_Units_Sold"]
            ).sort_values("Date")

            fig = px.line(
                forecast_plot,
                x="Date",
                y="Forecasted_Units_Sold",
                markers=True,
                title="Forecasted Daily Units"
            )
            fig.update_traces(line=dict(width=3))
            st.plotly_chart(
                prepare_plot(fig),
                use_container_width=True,
                key="overview_forecast"
            )
        else:
            missing_message("Demand Forecast")

    # CHURN AND INVENTORY CHARTS
    left, right = st.columns(2)

    with left:
        section_title("🔍 Churn Overview")

        if churn is not None and "Churn" in churn.columns:
            flags = churn_flags(churn)
            churn_dist = pd.DataFrame({
                "Status": ["Churn", "Non-Churn"],
                "Customers": [
                    int(flags.sum()),
                    int((~flags).sum())
                ]
            })

            fig = px.pie(
                churn_dist,
                names="Status",
                values="Customers",
                hole=0.62,
                title="Customer Churn Split"
            )
            fig.update_traces(
                textposition="inside",
                textinfo="label+percent"
            )
            st.plotly_chart(
                prepare_plot(fig),
                use_container_width=True,
                key="overview_churn"
            )
        else:
            missing_message("Churn Analysis")

    with right:
        section_title("📦 Inventory Reorder Summary")

        if (
            inventory is not None
            and "Recommended_Reorder_Qty" in inventory.columns
        ):
            inv = inventory.copy()
            inv["Recommended_Reorder_Qty"] = pd.to_numeric(
                inv["Recommended_Reorder_Qty"], errors="coerce"
            ).fillna(0)

            top = inv.nlargest(10, "Recommended_Reorder_Qty")

            if "SKU" in top.columns:
                fig = px.bar(
                    top.sort_values("Recommended_Reorder_Qty"),
                    x="Recommended_Reorder_Qty",
                    y="SKU",
                    orientation="h",
                    text="Recommended_Reorder_Qty",
                    title="Top 10 Reorder Quantities"
                )
                fig.update_traces(textposition="outside")
                st.plotly_chart(
                    prepare_plot(fig),
                    use_container_width=True,
                    key="overview_inventory"
                )
            else:
                missing_message("Inventory SKU column")
        else:
            missing_message("Inventory Recommendations")

    if inventory is not None and "Recommended_Reorder_Qty" in inventory.columns:
        st.divider()
        section_title("📦 Inventory Summary")

        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Total Recommended Reorder",
            f"{metric_value(inventory, 'Recommended_Reorder_Qty').sum():,.0f} units"
        )
        col2.metric("SKUs Needing Reorder", f"{reorder_count:,}")
        col3.metric("SKUs at Stockout Risk", f"{stockout_count:,}")

        st.caption(
            "Inventory metrics use the saved recommendations and latest "
            "inventory snapshot available in the dataset."
        )


# =========================================================
# CUSTOMER ANALYTICS
# =========================================================
elif page == "Customer Analytics":

    section_title(
        "👥 Customer Analytics",
        "Explore customer segments, RFM metrics and individual customer records."
    )

    if customers is None:
        missing_message("Customer Analytics")
    else:
        filtered = customers.copy()

        # Segment filter
        if "Segment" in filtered.columns:
            segment_options = ["All"] + sorted(
                filtered["Segment"].dropna().astype(str).unique().tolist()
            )

            chosen_segment = st.selectbox(
                "Filter by customer segment",
                segment_options
            )

            if chosen_segment != "All":
                filtered = filtered[
                    filtered["Segment"].astype(str) == chosen_segment
                ]

        # KPI row
        col1, col2, col3 = st.columns(3)
        col1.metric("Customers", f"{len(filtered):,}")

        col2.metric(
            "Segments",
            str(filtered["Segment"].nunique())
            if "Segment" in filtered.columns else "N/A"
        )

        if "Monetary" in filtered.columns:
            col3.metric(
                "Total Customer Monetary Value",
                f"{metric_value(filtered, 'Monetary').sum():,.0f}"
            )
        else:
            col3.metric("Customer Records", f"{len(filtered):,}")

        st.divider()

        left, right = st.columns(2)

        with left:
            if "Segment" in filtered.columns:
                section_title("Segment Distribution")

                segment_counts = (
                    filtered["Segment"].fillna("Unknown")
                    .value_counts()
                    .rename_axis("Segment")
                    .reset_index(name="Customers")
                )

                fig = px.bar(
                    segment_counts,
                    x="Segment",
                    y="Customers",
                    color="Segment",
                    text="Customers"
                )
                fig.update_traces(textposition="outside")
                fig.update_layout(showlegend=False)

                st.plotly_chart(
                    prepare_plot(fig),
                    use_container_width=True,
                    key="customer_segment_chart"
                )

        with right:
            if {"Frequency", "Monetary"}.issubset(filtered.columns):
                section_title("Purchase Frequency vs Monetary Value")

                plot_df = filtered.copy()
                plot_df["Frequency"] = pd.to_numeric(
                    plot_df["Frequency"], errors="coerce"
                )
                plot_df["Monetary"] = pd.to_numeric(
                    plot_df["Monetary"], errors="coerce"
                )
                plot_df = plot_df.dropna(
                    subset=["Frequency", "Monetary"]
                )

                fig = px.scatter(
                    plot_df,
                    x="Frequency",
                    y="Monetary",
                    color="Segment" if "Segment" in plot_df.columns else None,
                    hover_data=["CustomerID"]
                    if "CustomerID" in plot_df.columns else None,
                    title="Customer Purchase Behaviour"
                )

                st.plotly_chart(
                    prepare_plot(fig),
                    use_container_width=True,
                    key="customer_frequency_chart"
                )

        section_title("Customer Records")
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        download_csv(filtered, "customer_analytics_filtered.csv")


# =========================================================
# CHURN ANALYSIS
# =========================================================
elif page == "Churn Analysis":

    section_title(
        "🔍 Churn Analysis",
        "Understand churn distribution and filter customer records by status."
    )

    if churn is None:
        missing_message("Churn Analysis")

    elif "Churn" not in churn.columns:
        st.error("churn_data.csv mein 'Churn' column nahi mila.")
        st.dataframe(churn.head(), use_container_width=True)

    else:
        churn_df = churn.copy()
        churn_df["_IsChurn"] = churn_flags(churn_df)

        total = len(churn_df)
        churned = int(churn_df["_IsChurn"].sum())
        retained = total - churned
        rate = churned / total * 100 if total else 0

        a, b, c = st.columns(3)
        a.metric("Customers Analyzed", f"{total:,}")
        b.metric("Churned Customers", f"{churned:,}")
        c.metric("Churn Rate", f"{rate:.2f}%")

        st.divider()

        left, right = st.columns(2)

        with left:
            section_title("Churn Distribution")

            distribution = pd.DataFrame({
                "Customer Status": ["Churn", "Non-Churn"],
                "Customers": [churned, retained]
            })

            fig = px.bar(
                distribution,
                x="Customer Status",
                y="Customers",
                color="Customer Status",
                text="Customers",
                title="Churn vs Retained Customers"
            )
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_layout(
                showlegend=False,
                margin=dict(l=20, r=30, t=65, b=60),
                title=dict(text="Churn vs Retained Customers", x=0.02, xanchor="left")
            )
            fig.update_xaxes(title_text="Customer Status")
            fig.update_yaxes(title_text="Number of Customers", rangemode="tozero")

            st.plotly_chart(
                prepare_plot(fig, 400),
                use_container_width=True,
                key="churn_distribution_chart"
            )

        with right:
            section_title("Churn Proportion")

            pie_data = pd.DataFrame({
                "Status": ["Churn", "Non-Churn"],
                "Customers": [churned, retained]
            })

            fig = px.pie(
                pie_data,
                names="Status",
                values="Customers",
                hole=0.62
            )
            fig.update_traces(
                textinfo="label+percent",
                textposition="inside",
                insidetextorientation="horizontal",
                hole=0.62
            )
            fig.update_layout(
                showlegend=False,
                margin=dict(l=20, r=20, t=55, b=20),
                title=dict(text="Customer Churn Share", x=0.02, xanchor="left")
            )

            st.plotly_chart(
                prepare_plot(fig, 400),
                use_container_width=True,
                key="churn_pie_chart"
            )

        st.divider()
        section_title("Customer Records")

        status = st.selectbox(
            "Filter customer status",
            ["All", "Churn", "Non-Churn"]
        )

        visible = churn_df.copy()

        if status == "Churn":
            visible = visible[visible["_IsChurn"]]
        elif status == "Non-Churn":
            visible = visible[~visible["_IsChurn"]]

        visible = visible.drop(columns=["_IsChurn"])

        st.caption(f"Showing {len(visible):,} customer records.")
        st.dataframe(visible, use_container_width=True, hide_index=True)
        download_csv(visible, "churn_data_filtered.csv")


# =========================================================
# DEMAND FORECASTING
# =========================================================
elif page == "Demand Forecasting":

    section_title(
        "📈 Demand Forecasting",
        "Explore the saved forecast, select a date range and download forecast records."
    )

    if (
        forecast is None
        or not {"Date", "Forecasted_Units_Sold"}.issubset(forecast.columns)
    ):
        missing_message("Demand Forecast")

    else:
        forecast_df = forecast.copy()

        forecast_df["Date"] = pd.to_datetime(
            forecast_df["Date"], errors="coerce"
        )
        forecast_df["Forecasted_Units_Sold"] = pd.to_numeric(
            forecast_df["Forecasted_Units_Sold"], errors="coerce"
        )

        forecast_df = forecast_df.dropna(
            subset=["Date", "Forecasted_Units_Sold"]
        ).sort_values("Date")

        if forecast_df.empty:
            st.warning("Forecast file mein valid records nahi mile.")
        else:
            st.markdown("### 📅 Forecast Period")
            st.caption(
                "Date filter sirf saved forecast records ke andar ka period select karta hai. "
                "Is file mein jitni dates saved hain, usse aage ke months dikhane ke liye "
                "forecast model se additional predictions generate karni hongi."
            )

            min_date = forecast_df["Date"].min().date()
            max_date = forecast_df["Date"].max().date()

            date_range = st.date_input(
                "Select forecast date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

            filtered_forecast = forecast_df.copy()

            if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
                start_date, end_date = date_range

                filtered_forecast = forecast_df[
                    forecast_df["Date"].dt.date.between(
                        start_date, end_date
                    )
                ].copy()

            total_units = filtered_forecast[
                "Forecasted_Units_Sold"
            ].sum()

            average_units = filtered_forecast[
                "Forecasted_Units_Sold"
            ].mean()

            peak_units = filtered_forecast[
                "Forecasted_Units_Sold"
            ].max()

            a, b, c, d = st.columns(4)

            a.metric("Forecast Horizon", f"{len(filtered_forecast)} days")
            b.metric("Total Forecast", f"{total_units:,.0f} units")
            c.metric(
                "Average Daily Forecast",
                f"{average_units:,.1f}" if pd.notna(average_units) else "N/A"
            )
            d.metric(
                "Peak Daily Forecast",
                f"{peak_units:,.1f}" if pd.notna(peak_units) else "N/A"
            )

            st.divider()

            section_title("Daily Forecast Trend")

            fig = px.line(
                filtered_forecast,
                x="Date",
                y="Forecasted_Units_Sold",
                markers=True,
                title="Forecasted Units by Date"
            )
            fig.update_traces(
                line=dict(width=3),
                marker=dict(size=6),
                hovertemplate="Date: %{x|%d %b %Y}<br>Forecast: %{y:,.1f} units<extra></extra>"
            )
            fig.update_xaxes(tickformat="%d %b", tickangle=-25, nticks=10)
            fig.update_yaxes(title_text="Forecasted Units")

            st.plotly_chart(
                prepare_plot(fig, 420),
                use_container_width=True,
                key="forecast_trend_chart"
            )

            section_title("Forecast Records")

            st.dataframe(
                filtered_forecast,
                use_container_width=True,
                hide_index=True
            )
            download_csv(
                filtered_forecast,
                "forecast_30_days_filtered.csv"
            )

            st.caption(
                "Forecast values come from the saved model output. "
                "They represent forecast estimates, not actual sales."
            )


# =========================================================
# INVENTORY OPTIMIZATION
# =========================================================
elif page == "Inventory Optimization":

    section_title(
        "📦 Inventory Optimization",
        "Review reorder recommendations, available stock and potential stockout risks."
    )

    if inventory is None:
        missing_message("Inventory Recommendations")

    elif "Recommended_Reorder_Qty" not in inventory.columns:
        st.error(
            "inventory_recommendations.csv mein "
            "Recommended_Reorder_Qty column nahi mila."
        )
        st.dataframe(inventory.head(), use_container_width=True)

    else:
        inv = inventory.copy()

        inv["Recommended_Reorder_Qty"] = pd.to_numeric(
            inv["Recommended_Reorder_Qty"], errors="coerce"
        ).fillna(0)

        reorder_count = int(
            (inv["Recommended_Reorder_Qty"] > 0).sum()
        )
        total_reorder = inv["Recommended_Reorder_Qty"].sum()

        risk_flags = stockout_flags(inv)
        stockout_count = int(risk_flags.sum()) if len(risk_flags) else 0

        if "Current_Stock" in inv.columns:
            current_stock_total = metric_value(
                inv, "Current_Stock"
            ).sum()
        else:
            current_stock_total = None

        a, b, c, d = st.columns(4)

        a.metric("Total SKUs", f"{len(inv):,}")
        b.metric("SKUs Needing Reorder", f"{reorder_count:,}")
        c.metric("Total Reorder Quantity", f"{total_reorder:,.0f} units")
        d.metric("Stockout Risk SKUs", f"{stockout_count:,}")

        if current_stock_total is not None:
            st.caption(
                f"Current recorded stock across listed SKUs: "
                f"{current_stock_total:,.0f} units."
            )

        st.divider()

        left, right = st.columns(2)

        with left:
            section_title("Top 10 Reorder Recommendations")

            if "SKU" in inv.columns:
                top = inv.nlargest(10, "Recommended_Reorder_Qty").copy()
                top = top.sort_values("Recommended_Reorder_Qty")

                fig = px.bar(
                    top,
                    x="Recommended_Reorder_Qty",
                    y="SKU",
                    orientation="h",
                    text="Recommended_Reorder_Qty",
                    title="Recommended Units to Reorder"
                )
                fig.update_traces(textposition="outside")

                st.plotly_chart(
                    prepare_plot(fig, 420),
                    use_container_width=True,
                    key="inventory_reorder_chart"
                )
            else:
                st.warning("Inventory file mein SKU column nahi mila.")

        with right:
            section_title("Current Stock vs Estimated 30-Day Demand")

            needed_columns = {
                "SKU", "Current_Stock", "Forecast_30_Days"
            }

            if needed_columns.issubset(inv.columns):
                stock_plot = inv.copy()

                stock_plot["Current_Stock"] = pd.to_numeric(
                    stock_plot["Current_Stock"], errors="coerce"
                )
                stock_plot["Forecast_30_Days"] = pd.to_numeric(
                    stock_plot["Forecast_30_Days"], errors="coerce"
                )

                stock_plot = stock_plot.dropna(
                    subset=["Current_Stock", "Forecast_30_Days"]
                ).nlargest(10, "Recommended_Reorder_Qty")

                fig = go.Figure()

                fig.add_trace(go.Bar(
                    x=stock_plot["SKU"],
                    y=stock_plot["Current_Stock"],
                    name="Current Stock"
                ))

                fig.add_trace(go.Bar(
                    x=stock_plot["SKU"],
                    y=stock_plot["Forecast_30_Days"],
                    name="Estimated 30-Day Demand"
                ))

                fig.update_layout(
                    barmode="group",
                    title="Stock vs Estimated Demand"
                )

                st.plotly_chart(
                    prepare_plot(fig, 420),
                    use_container_width=True,
                    key="inventory_stock_demand_chart"
                )
            else:
                st.info(
                    "Stock comparison graph ke liye Current_Stock aur "
                    "Forecast_30_Days columns required hain."
                )

        st.divider()

        section_title("Inventory Records & Filters")

        col1, col2 = st.columns([2, 1])

        with col1:
            sku_search = st.text_input(
                "Search SKU",
                placeholder="e.g. SKU012"
            )

        with col2:
            reorder_only = st.checkbox(
                "Show only SKUs needing reorder"
            )

        visible = inv.copy()

        if "SKU" in visible.columns and sku_search.strip():
            visible = visible[
                visible["SKU"].astype(str).str.contains(
                    sku_search.strip(),
                    case=False,
                    na=False
                )
            ]

        if reorder_only:
            visible = visible[
                visible["Recommended_Reorder_Qty"] > 0
            ]

        visible = visible.sort_values(
            "Recommended_Reorder_Qty",
            ascending=False
        )

        st.caption(f"Showing {len(visible):,} SKUs.")
        st.dataframe(
            visible,
            use_container_width=True,
            hide_index=True
        )

        download_csv(
            visible,
            "inventory_recommendations_filtered.csv"
        )

        st.caption(
            "Recommendations use the saved inventory analysis and forecast "
            "assumptions. Validate quantities before making purchasing decisions."
        )
