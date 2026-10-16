# RetailPulse 🛒
### AI-Powered E-commerce Business Analyst Agent

RetailPulse is a data-driven analytics project designed to help businesses understand customers, analyze churn, forecast product demand, and optimize inventory through an interactive Streamlit dashboard.

## 🚀 Features

- **Executive Overview** — Key business performance indicators.
- **Customer Analytics** — RFM analysis and customer segmentation.
- **Churn Analysis** — Customer churn data and model-based analysis.
- **Demand Forecasting** — Historical sales analysis and 30-day demand forecasts.
- **Inventory Optimization** — Stock analysis, stockout risk, and reorder recommendations.

## 🛠️ Technology Stack

Python · Streamlit · Pandas · Scikit-learn · Plotly · Matplotlib · Git · GitHub

## 📁 Project Structure

- `dashboard/` — Streamlit application
- `data/customer/` — Customer analytics and churn outputs
- `data/raw/` — Source datasets
- `data/processed/` — Processed datasets, forecasts, models, and inventory outputs
- `notebooks/` — Data preparation, forecasting, and inventory scripts
- `requirements.txt` — Python dependencies

## ⚙️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/itsaman-ux/RetailPulse.git
cd RetailPulse
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Launch the dashboard

```bash
streamlit run dashboard/app.py
```

Open the local URL shown in the terminal.

## 👥 Team

- **Aman** — Demand forecasting and integration
- **Ritesh** — Customer analytics, segmentation, and churn prediction
- **Durga** — Inventory optimization
- **Aditya** — Dashboard and deployment

## 📌 Project Status

The five main dashboard sections have been tested locally. Team collaboration, final validation, documentation, and public deployment are ongoing tasks.

## 🔮 Future Improvements

- Improve model validation and evaluation
- Refine demand forecasting and inventory recommendations
- Add automated testing
- Deploy the dashboard publicly
- Expand technical documentation

## 🔗 Repository

https://github.com/itsaman-ux/RetailPulse
