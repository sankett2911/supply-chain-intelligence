import pandas as pd
import numpy as np
import os
from datetime import date, timedelta

np.random.seed(55)

INDUSTRIES = ['Electronics', 'Grocery', 'Apparel', 'Healthcare', 'Automotive', 'Industrial']
REGIONS = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East']
SUPPLIER_TIERS = ['Tier 1', 'Tier 2', 'Tier 3']

INDUSTRY_CONFIG = {
    'Electronics':  {'margin': 0.28, 'lead_days': 21, 'season': [0.9,0.85,0.9,0.92,0.95,0.95,1.0,1.02,1.0,1.05,1.12,1.35]},
    'Grocery':      {'margin': 0.18, 'lead_days': 7,  'season': [0.96,0.94,0.97,1.0,1.02,1.05,1.08,1.06,1.02,1.0,1.01,1.04]},
    'Apparel':      {'margin': 0.45, 'lead_days': 45, 'season': [0.75,0.70,0.85,1.0,1.08,0.95,0.88,0.90,1.02,1.08,1.18,1.28]},
    'Healthcare':   {'margin': 0.55, 'lead_days': 14, 'season': [1.05,1.02,1.0,0.98,0.97,0.96,0.97,0.98,1.0,1.02,1.04,1.06]},
    'Automotive':   {'margin': 0.22, 'lead_days': 30, 'season': [0.88,0.85,0.90,0.95,1.05,1.08,1.1,1.1,1.05,1.0,0.95,0.9]},
    'Industrial':   {'margin': 0.32, 'lead_days': 18, 'season': [0.92,0.90,0.95,1.0,1.05,1.08,1.05,1.03,1.0,0.98,0.95,0.92]},
}

YEARS = [2022, 2023, 2024]
START = date(2022, 1, 3)
END = date(2024, 12, 30)


def generate_suppliers(n=220):
    rows = []
    for i in range(n):
        ind = np.random.choice(INDUSTRIES)
        tier = np.random.choice(SUPPLIER_TIERS, p=[0.25, 0.45, 0.30])
        quality = np.random.beta(8, 2)  # skew high
        rows.append({
            'SUPPLIER_ID': f'SUP{1000+i}',
            'SUPPLIER_NAME': f'{ind} Supplier {i+1}',
            'INDUSTRY': ind,
            'REGION': np.random.choice(REGIONS),
            'TIER': tier,
            'QUALITY_SCORE': round(quality * 100, 1),
            'ON_TIME_DELIVERY_BASE': round(np.random.uniform(0.72, 0.98), 3),
            'DEFECT_RATE_BASE': round(np.random.uniform(0.005, 0.08), 4),
            'AVG_LEAD_DAYS': int(np.random.normal(INDUSTRY_CONFIG[ind]['lead_days'], 5)),
            'ANNUAL_SPEND': round(np.random.lognormal(13, 1.2), 0),
            'SINGLE_SOURCE': int(np.random.random() < 0.18),
            'CONTRACTS_ACTIVE': np.random.randint(1, 8),
            'RISK_LEVEL': np.random.choice(['Low', 'Medium', 'High'], p=[0.55, 0.30, 0.15]),
        })
    return pd.DataFrame(rows)


def generate_skus(suppliers_df, n=500):
    rows = []
    for i in range(n):
        ind = np.random.choice(INDUSTRIES)
        sup_pool = suppliers_df[suppliers_df['INDUSTRY'] == ind]['SUPPLIER_ID'].tolist()
        if not sup_pool:
            sup_pool = suppliers_df['SUPPLIER_ID'].tolist()
        primary_sup = np.random.choice(sup_pool)
        unit_cost = np.random.lognormal(3.5, 1.2)
        reorder_point = int(np.random.uniform(50, 500))
        rows.append({
            'SKU_ID': f'SKU{10000+i}',
            'SKU_NAME': f'{ind} Product {i+1}',
            'INDUSTRY': ind,
            'CATEGORY': np.random.choice(['Raw Material', 'Component', 'Finished Good', 'Packaging'], p=[0.25, 0.35, 0.25, 0.15]),
            'PRIMARY_SUPPLIER': primary_sup,
            'UNIT_COST': round(unit_cost, 2),
            'REORDER_POINT': reorder_point,
            'SAFETY_STOCK': int(reorder_point * np.random.uniform(0.2, 0.5)),
            'MAX_STOCK': int(reorder_point * np.random.uniform(3, 8)),
            'LEAD_TIME_DAYS': int(np.random.normal(INDUSTRY_CONFIG[ind]['lead_days'], 5)),
            'CRITICALITY': np.random.choice(['Critical', 'High', 'Medium', 'Low'], p=[0.15, 0.25, 0.35, 0.25]),
        })
    return pd.DataFrame(rows)


def generate_weekly_inventory(skus_df):
    weeks = []
    d = START
    while d <= END:
        weeks.append(d)
        d += timedelta(weeks=1)

    rows = []
    for _, sku in skus_df.iterrows():
        ind = sku['INDUSTRY']
        cfg = INDUSTRY_CONFIG[ind]
        base_demand = np.random.uniform(80, 600)
        current_stock = int(sku['MAX_STOCK'] * np.random.uniform(0.4, 0.9))
        trend = np.random.uniform(-0.001, 0.003)

        for wk in weeks:
            month_idx = wk.month - 1
            season = cfg['seasonality'][month_idx] if 'seasonality' in cfg else cfg['season'][month_idx]
            year_mult = 1 + 0.07 * (wk.year - 2022)
            noise = np.random.normal(1.0, 0.12)
            weekly_demand = max(1, int(base_demand * season * year_mult * noise * (1 + trend * (wk - START).days)))

            # Simulate replenishment
            if current_stock < sku['REORDER_POINT']:
                replenishment = int(sku['MAX_STOCK'] * np.random.uniform(0.6, 1.0))
            else:
                replenishment = 0

            stockout = int(current_stock <= 0)
            fulfilled = min(weekly_demand, max(0, current_stock))
            current_stock = max(0, current_stock + replenishment - weekly_demand)
            current_stock = min(current_stock, int(sku['MAX_STOCK'] * 1.1))

            dos = round(current_stock / max(1, weekly_demand) * 7, 1)

            rows.append({
                'SKU_ID': sku['SKU_ID'],
                'WEEK_START': wk.strftime('%Y-%m-%d'),
                'YEAR': wk.year,
                'MONTH': wk.month,
                'INDUSTRY': ind,
                'STOCK_LEVEL': current_stock,
                'WEEKLY_DEMAND': weekly_demand,
                'WEEKLY_FULFILLED': fulfilled,
                'REPLENISHMENT': replenishment,
                'STOCKOUT': stockout,
                'DAYS_OF_SUPPLY': min(dos, 180),
                'REORDER_TRIGGERED': int(replenishment > 0),
                'FILL_RATE': round(fulfilled / max(1, weekly_demand), 4),
            })
    return pd.DataFrame(rows)


def generate_supplier_performance(suppliers_df):
    weeks = []
    d = START
    while d <= END:
        weeks.append(d)
        d += timedelta(weeks=1)

    rows = []
    for _, sup in suppliers_df.iterrows():
        otd_base = sup['ON_TIME_DELIVERY_BASE']
        defect_base = sup['DEFECT_RATE_BASE']
        lead_base = sup['AVG_LEAD_DAYS']
        trend = np.random.choice([-0.0002, 0, 0.0001], p=[0.2, 0.6, 0.2])

        for wk in weeks[::2]:  # bi-weekly
            days_elapsed = (wk - START).days
            otd = min(1.0, max(0.4, otd_base + trend * days_elapsed + np.random.normal(0, 0.03)))
            defect = max(0, defect_base + np.random.normal(0, defect_base * 0.2))
            lead = max(1, int(lead_base + np.random.normal(0, 3)))
            orders = np.random.randint(3, 25)
            spend = round(np.random.lognormal(10, 0.8), 0)
            rows.append({
                'SUPPLIER_ID': sup['SUPPLIER_ID'],
                'INDUSTRY': sup['INDUSTRY'],
                'REGION': sup['REGION'],
                'TIER': sup['TIER'],
                'WEEK_START': wk.strftime('%Y-%m-%d'),
                'YEAR': wk.year,
                'ON_TIME_DELIVERY': round(otd, 4),
                'DEFECT_RATE': round(defect, 4),
                'LEAD_TIME_DAYS': lead,
                'ORDERS_PLACED': orders,
                'SPEND': spend,
                'SCORE': round((otd * 0.4 + (1 - defect * 10) * 0.35 + min(1, lead_base / max(1, lead)) * 0.25) * 100, 1),
            })
    return pd.DataFrame(rows)


def generate_forecast(inventory_df, skus_df):
    rows = []
    for sku_id in skus_df['SKU_ID'].unique()[:100]:  # top 100 SKUs
        sku_data = inventory_df[inventory_df['SKU_ID'] == sku_id].sort_values('WEEK_START')
        if len(sku_data) < 52:
            continue
        demands = sku_data['WEEKLY_DEMAND'].values
        ind = sku_data['INDUSTRY'].iloc[0]
        cfg = INDUSTRY_CONFIG[ind]

        # Simple trend + seasonal forecast
        trend = np.polyfit(range(len(demands)), demands, 1)[0]
        base = demands[-12:].mean()
        last_date = date.fromisoformat(sku_data['WEEK_START'].iloc[-1])

        for w in range(1, 13):
            fcast_date = last_date + timedelta(weeks=w)
            month_idx = fcast_date.month - 1
            season = cfg['season'][month_idx]
            forecast = max(1, int((base + trend * w) * season * np.random.normal(1.0, 0.05)))
            lower = int(forecast * 0.82)
            upper = int(forecast * 1.18)
            rows.append({
                'SKU_ID': sku_id,
                'INDUSTRY': ind,
                'FORECAST_DATE': fcast_date.strftime('%Y-%m-%d'),
                'FORECAST_WEEK': w,
                'DEMAND_FORECAST': forecast,
                'LOWER_BOUND': lower,
                'UPPER_BOUND': upper,
                'TREND': round(trend, 3),
            })
    return pd.DataFrame(rows)


if __name__ == '__main__':
    print("Generating suppliers...")
    sup_df = generate_suppliers()
    print(f"  {len(sup_df)} suppliers across {sup_df['INDUSTRY'].nunique()} industries")

    print("Generating SKUs...")
    sku_df = generate_skus(sup_df)
    print(f"  {len(sku_df)} SKUs")

    print("Generating weekly inventory (3 years)...")
    inv_df = generate_weekly_inventory(sku_df)
    print(f"  {len(inv_df):,} inventory records | Avg fill rate: {inv_df['FILL_RATE'].mean():.1%}")

    print("Generating supplier performance...")
    perf_df = generate_supplier_performance(sup_df)
    print(f"  {len(perf_df):,} supplier performance records")

    print("Generating demand forecasts...")
    fcast_df = generate_forecast(inv_df, sku_df)
    print(f"  {len(fcast_df):,} forecast records")

    os.makedirs('data', exist_ok=True)
    sup_df.to_csv('data/suppliers.csv', index=False)
    sku_df.to_csv('data/skus.csv', index=False)
    inv_df.to_csv('data/inventory.csv', index=False)
    perf_df.to_csv('data/supplier_performance.csv', index=False)
    fcast_df.to_csv('data/forecast.csv', index=False)
    print("\nAll data saved to data/")
