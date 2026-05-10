# Supply Chain Intelligence Dashboard

**🔴 Live Demo → [supply-chain-intelligence.streamlit.app](https://supply-chain-intelligence-kbkgrbuano985ixgrstekg.streamlit.app)**

An end-to-end supply chain analytics dashboard covering inventory management, supplier performance, demand forecasting, and risk analysis across 220 suppliers, 500+ SKUs, and 3 years of weekly data spanning 6 industries.

**Built by Sanket Patil** — [LinkedIn](https://linkedin.com/in/sanketkbpatil) | [Tableau](https://public.tableau.com/app/profile/sanket.patil1424/vizzes)

---

## Features

- **Overview** — KPIs: fill rate, OTD, stockout rate, defect rate, total spend. Spend by industry, supplier distribution, fill rate trend, OTD by region
- **Inventory** — Days of supply by industry, stockout heatmap by month, SKU-level inventory status with reorder alerts
- **Supplier Performance** — OTD trend by industry, defect rate by tier, lead time distribution, full supplier scorecard
- **Demand Forecasting** — 12-week forward forecast with confidence bands per SKU, industry-level forecast, trend direction analysis
- **Risk & Alerts** — High-risk supplier flags, single-source dependency list, at-risk SKU table, spend concentration analysis

---

## Local Setup

```bash
git clone https://github.com/sankett2911/supply-chain-intelligence
cd supply-chain-intelligence
pip install -r requirements.txt
python generate_data.py
streamlit run app.py
```

---

## Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to share.streamlit.io → Deploy a public app from GitHub
3. Select repo, set main file to `app.py`, deploy

---

## Tech Stack

Python · Pandas · Plotly · Streamlit
