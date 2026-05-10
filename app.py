import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

st.set_page_config(page_title="Supply Chain Intelligence", page_icon="🔗", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
  .metric-card{background:#f0f7ff;border-radius:10px;padding:16px 20px;border-left:4px solid #1a6fd4}
  .metric-card.green{background:#f0fdf4;border-left-color:#16a34a}
  .metric-card.amber{background:#fffbeb;border-left-color:#d97706}
  .metric-card.red{background:#fff1f2;border-left-color:#e11d48}
  .metric-card.purple{background:#faf5ff;border-left-color:#7c3aed}
  .metric-value{font-size:26px;font-weight:700;color:#111827}
  .metric-label{font-size:12px;color:#6b7280;margin-top:3px}
  .sec{font-size:14px;font-weight:600;color:#111827;margin-bottom:8px;padding-bottom:5px;border-bottom:1px solid #e5e7eb}
  .alert-high{background:#fff1f2;border:1px solid #fecdd3;border-radius:8px;padding:10px 14px;margin-bottom:6px;font-size:13px}
  .alert-med{background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:10px 14px;margin-bottom:6px;font-size:13px}
  div[data-testid="stSidebar"]{background:#f8faff}
</style>""", unsafe_allow_html=True)

IND_COLORS = {'Electronics':'#2563eb','Grocery':'#16a34a','Apparel':'#e11d48','Healthcare':'#7c3aed','Automotive':'#d97706','Industrial':'#0891b2'}
TIER_COLORS = {'Tier 1':'#1a6fd4','Tier 2':'#0891b2','Tier 3':'#6b7280'}
RISK_COLORS = {'Low':'#16a34a','Medium':'#d97706','High':'#e11d48'}

@st.cache_data
def load_data():
    if not os.path.exists('data/suppliers.csv'):
        st.error("Run `python generate_data.py` first.")
        st.stop()
    suppliers = pd.read_csv('data/suppliers.csv')
    skus = pd.read_csv('data/skus.csv')
    inventory = pd.read_csv('data/inventory.csv', parse_dates=['WEEK_START'])
    perf = pd.read_csv('data/supplier_performance.csv', parse_dates=['WEEK_START'])
    forecast = pd.read_csv('data/forecast.csv', parse_dates=['FORECAST_DATE'])
    return suppliers, skus, inventory, perf, forecast

suppliers, skus, inventory, perf, forecast = load_data()

with st.expander("👋 Welcome — How to use this dashboard", expanded=False):
    st.markdown("""
    This dashboard provides end-to-end supply chain visibility across **220 suppliers, 500+ SKUs, and 3 years of weekly data** spanning 6 industries — Electronics, Grocery, Apparel, Healthcare, Automotive, and Industrial. It mirrors the analytics used by supply chain teams at companies like Lowe's, Amazon, Cardinal Health, and GE.

    **Start here:**
    - **Overview** — Top-line KPIs: fill rates, stockout rates, supplier OTD, total spend
    - **Inventory** — Stock levels by SKU, days of supply, stockout risk heatmap, reorder alerts
    - **Supplier Performance** — OTD trends, defect rates, lead time analysis, supplier scorecards
    - **Demand Forecasting** — 12-week forward forecast with confidence bands per SKU, trend decomposition
    - **Risk & Alerts** — At-risk SKUs, single-source dependencies, supplier concentration, high-risk flags

    **Try these:**
    - Filter to **Healthcare** → check supplier OTD — critical supply chains have tighter tolerances
    - In Inventory, sort by **Days of Supply ascending** to find stockout-risk SKUs
    - In Supplier Performance, filter to **Tier 1** vs **Tier 3** — the performance gap tells a story
    - In Forecasting, select an **Apparel SKU** — watch the December seasonality spike
    - In Risk & Alerts, filter to **Single Source = Yes** — these are your most vulnerable SKUs

    **Stack:** Python · Pandas · Plotly · Streamlit
    &nbsp;|&nbsp; **Built by** [Sanket Patil](https://linkedin.com/in/sanketkbpatil)
    &nbsp;|&nbsp; [GitHub](https://github.com/sankett2911/supply-chain-intelligence)
    """)

with st.sidebar:
    st.markdown("## 🔗 Supply Chain Intelligence")
    st.markdown("*220 Suppliers · 500+ SKUs · 3 Years*")
    st.markdown("---")
    ind_opts = ["All Industries"] + sorted(suppliers['INDUSTRY'].unique())
    sel_ind = st.selectbox("Industry", ind_opts)
    region_opts = ["All Regions"] + sorted(suppliers['REGION'].unique())
    sel_region = st.selectbox("Region", region_opts)
    tier_opts = ["All Tiers"] + sorted(suppliers['TIER'].unique())
    sel_tier = st.selectbox("Supplier Tier", tier_opts)
    year_opts = ["All Years", 2022, 2023, 2024]
    sel_year = st.selectbox("Year", year_opts)
    st.markdown("---")
    st.caption("Built by Sanket Patil")
    st.markdown("[GitHub](https://github.com/sankett2911) | [LinkedIn](https://linkedin.com/in/sanketkbpatil)")

def fsup(df):
    f = df.copy()
    if sel_ind != "All Industries": f = f[f['INDUSTRY'] == sel_ind]
    if sel_region != "All Regions": f = f[f['REGION'] == sel_region]
    if sel_tier != "All Tiers": f = f[f['TIER'] == sel_tier]
    return f

def finv(df):
    f = df.copy()
    if sel_ind != "All Industries": f = f[f['INDUSTRY'] == sel_ind]
    if sel_year != "All Years": f = f[f['YEAR'] == sel_year]
    return f

def fperf(df):
    f = df.copy()
    if sel_ind != "All Industries": f = f[f['INDUSTRY'] == sel_ind]
    if sel_region != "All Regions": f = f[f['REGION'] == sel_region]
    if sel_tier != "All Tiers": f = f[f['TIER'] == sel_tier]
    if sel_year != "All Years": f = f[f['YEAR'] == sel_year]
    return f

filt_sup = fsup(suppliers)
filt_inv = finv(inventory)
filt_perf = fperf(perf)
filt_sup_ids = filt_sup['SUPPLIER_ID'].tolist()

avg_otd = filt_perf['ON_TIME_DELIVERY'].mean()
avg_defect = filt_perf['DEFECT_RATE'].mean()
avg_fill = filt_inv['FILL_RATE'].mean()
stockout_rate = filt_inv['STOCKOUT'].mean()
total_spend = filt_perf['SPEND'].sum()

st.title("Supply Chain Intelligence Dashboard")
st.markdown(f"**{len(filt_sup):,} suppliers** · **{sel_ind if sel_ind != 'All Industries' else 'All Industries'}** · {sel_year if sel_year != 'All Years' else '2022–2024'}")

c1,c2,c3,c4,c5 = st.columns(5)
with c1: st.markdown(f'<div class="metric-card green"><div class="metric-value">{avg_fill*100:.1f}%</div><div class="metric-label">Avg Fill Rate</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_otd*100:.1f}%</div><div class="metric-label">On-Time Delivery</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-card amber"><div class="metric-value">{stockout_rate*100:.1f}%</div><div class="metric-label">Stockout Rate</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="metric-card red"><div class="metric-value">{avg_defect*100:.2f}%</div><div class="metric-label">Avg Defect Rate</div></div>', unsafe_allow_html=True)
with c5: st.markdown(f'<div class="metric-card purple"><div class="metric-value">${total_spend/1e6:.1f}M</div><div class="metric-label">Total Spend</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
tab1,tab2,tab3,tab4,tab5 = st.tabs(["📊 Overview","📦 Inventory","🏭 Supplier Performance","📈 Demand Forecasting","⚠️ Risk & Alerts"])

with tab1:
    r1c1,r1c2 = st.columns(2)
    with r1c1:
        st.markdown('<div class="sec">Spend by Industry</div>', unsafe_allow_html=True)
        spend_ind = filt_perf.groupby('INDUSTRY')['SPEND'].sum().reset_index()
        fig = px.bar(spend_ind.sort_values('SPEND'), x='SPEND', y='INDUSTRY', orientation='h',
                     color='INDUSTRY', color_discrete_map=IND_COLORS, labels={'SPEND':'Total Spend ($)','INDUSTRY':''})
        fig.update_layout(height=300, margin=dict(t=10,b=10,l=10,r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with r1c2:
        st.markdown('<div class="sec">Supplier Distribution by Tier</div>', unsafe_allow_html=True)
        tier_cnt = filt_sup.groupby(['TIER','INDUSTRY']).size().reset_index(name='count')
        fig2 = px.bar(tier_cnt, x='TIER', y='count', color='INDUSTRY', color_discrete_map=IND_COLORS,
                      labels={'count':'Suppliers','TIER':'Tier'})
        fig2.update_layout(height=300, margin=dict(t=10,b=10,l=10,r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)
    r2c1,r2c2 = st.columns(2)
    with r2c1:
        st.markdown('<div class="sec">Monthly Fill Rate Trend</div>', unsafe_allow_html=True)
        inv_monthly = filt_inv.copy()
        inv_monthly['MONTH_START'] = inv_monthly['WEEK_START'].dt.to_period('M').dt.to_timestamp()
        monthly_fill = inv_monthly.groupby('MONTH_START')['FILL_RATE'].mean().reset_index()
        fig3 = go.Figure(go.Scatter(x=monthly_fill['MONTH_START'], y=monthly_fill['FILL_RATE']*100,
                                     mode='lines+markers', line=dict(color='#16a34a',width=2.5),
                                     fill='tozeroy', fillcolor='rgba(22,163,74,0.07)'))
        fig3.update_layout(height=280, margin=dict(t=10,b=10,l=10,r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', yaxis_title='Fill Rate (%)', showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
    with r2c2:
        st.markdown('<div class="sec">OTD by Region</div>', unsafe_allow_html=True)
        otd_region = filt_perf.groupby('REGION')['ON_TIME_DELIVERY'].mean().reset_index()
        otd_region['OTD_PCT'] = (otd_region['ON_TIME_DELIVERY']*100).round(1)
        fig4 = px.bar(otd_region.sort_values('OTD_PCT'), x='OTD_PCT', y='REGION', orientation='h',
                      color='OTD_PCT', color_continuous_scale=['#fecaca','#16a34a'],
                      labels={'OTD_PCT':'On-Time Delivery (%)','REGION':''}, text='OTD_PCT')
        fig4.update_traces(texttemplate='%{text}%', textposition='outside')
        fig4.update_layout(height=280, margin=dict(t=10,b=10,l=10,r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True)

with tab2:
    st.markdown('<div class="sec">Inventory Health by Industry</div>', unsafe_allow_html=True)
    inv_ind = filt_inv.groupby('INDUSTRY').agg(
        avg_stock=('STOCK_LEVEL','mean'), avg_dos=('DAYS_OF_SUPPLY','mean'),
        stockout_rate=('STOCKOUT','mean'), avg_fill=('FILL_RATE','mean')
    ).reset_index().round(2)
    inv_ind['stockout_pct'] = (inv_ind['stockout_rate']*100).round(1)
    inv_ind['fill_pct'] = (inv_ind['avg_fill']*100).round(1)
    r1c1,r1c2 = st.columns(2)
    with r1c1:
        fig5 = px.bar(inv_ind.sort_values('avg_dos'), x='avg_dos', y='INDUSTRY', orientation='h',
                      color='INDUSTRY', color_discrete_map=IND_COLORS,
                      labels={'avg_dos':'Avg Days of Supply','INDUSTRY':''}, title='Avg Days of Supply by Industry')
        fig5.update_layout(height=300, margin=dict(t=30,b=10,l=10,r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)
    with r1c2:
        fig6 = px.bar(inv_ind.sort_values('stockout_pct', ascending=False), x='INDUSTRY', y='stockout_pct',
                      color='INDUSTRY', color_discrete_map=IND_COLORS,
                      labels={'stockout_pct':'Stockout Rate (%)','INDUSTRY':''}, title='Stockout Rate by Industry')
        fig6.update_layout(height=300, margin=dict(t=30,b=10,l=10,r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig6, use_container_width=True)

    st.markdown('<div class="sec">Weekly Stockout Heatmap (by Industry & Month)</div>', unsafe_allow_html=True)
    heat_data = filt_inv.copy()
    heat_data['MONTH'] = heat_data['WEEK_START'].dt.month
    heat_agg = heat_data.groupby(['INDUSTRY','MONTH'])['STOCKOUT'].mean().reset_index()
    heat_pivot = heat_agg.pivot(index='INDUSTRY', columns='MONTH', values='STOCKOUT')
    month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    heat_pivot.columns = [month_names[c-1] for c in heat_pivot.columns]
    fig7 = px.imshow(heat_pivot, color_continuous_scale=['#f0fdf4','#fef2f2','#e11d48'],
                     aspect='auto', labels={'color':'Stockout Rate'}, text_auto='.1%')
    fig7.update_layout(height=280, margin=dict(t=10,b=10,l=10,r=10), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig7, use_container_width=True)

    st.markdown('<div class="sec">SKU-Level Inventory Status (Latest Week)</div>', unsafe_allow_html=True)
    latest_inv = filt_inv.sort_values('WEEK_START').groupby('SKU_ID').last().reset_index()
    latest_inv = latest_inv.merge(skus[['SKU_ID','SKU_NAME','CRITICALITY','REORDER_POINT','SAFETY_STOCK']], on='SKU_ID')
    latest_inv['STATUS'] = latest_inv.apply(lambda r: '🔴 Stockout' if r['STOCKOUT'] else ('🟡 Low' if r['STOCK_LEVEL'] < r['REORDER_POINT'] else '🟢 OK'), axis=1)
    sort_opt = st.selectbox("Sort by", ['DAYS_OF_SUPPLY','FILL_RATE','STOCK_LEVEL'], format_func=lambda x: x.replace('_',' ').title())
    show = latest_inv.sort_values(sort_opt).head(50)[['SKU_NAME','INDUSTRY','CRITICALITY','STOCK_LEVEL','DAYS_OF_SUPPLY','FILL_RATE','STATUS']].copy()
    show['FILL_RATE'] = (show['FILL_RATE']*100).round(1).astype(str)+'%'
    show['DAYS_OF_SUPPLY'] = show['DAYS_OF_SUPPLY'].round(1)
    show.columns = ['SKU','Industry','Criticality','Stock','Days of Supply','Fill Rate','Status']
    st.dataframe(show, use_container_width=True, height=340, hide_index=True)

with tab3:
    r1c1,r1c2 = st.columns(2)
    with r1c1:
        st.markdown('<div class="sec">On-Time Delivery Trend by Industry</div>', unsafe_allow_html=True)
        otd_trend = filt_perf.copy()
        otd_trend['MONTH_START'] = otd_trend['WEEK_START'].dt.to_period('M').dt.to_timestamp()
        otd_monthly = otd_trend.groupby(['MONTH_START','INDUSTRY'])['ON_TIME_DELIVERY'].mean().reset_index()
        fig8 = px.line(otd_monthly, x='MONTH_START', y='ON_TIME_DELIVERY', color='INDUSTRY',
                       color_discrete_map=IND_COLORS, markers=False,
                       labels={'ON_TIME_DELIVERY':'OTD Rate','MONTH_START':'Month'})
        fig8.update_yaxes(tickformat='.0%')
        fig8.update_layout(height=300, margin=dict(t=10,b=10,l=10,r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig8, use_container_width=True)
    with r1c2:
        st.markdown('<div class="sec">Defect Rate by Supplier Tier</div>', unsafe_allow_html=True)
        defect_tier = filt_perf.groupby('TIER').agg(avg_defect=('DEFECT_RATE','mean'), avg_otd=('ON_TIME_DELIVERY','mean')).reset_index()
        defect_tier['defect_pct'] = (defect_tier['avg_defect']*100).round(3)
        fig9 = px.bar(defect_tier, x='TIER', y='defect_pct', color='TIER',
                      color_discrete_map=TIER_COLORS, text='defect_pct',
                      labels={'defect_pct':'Avg Defect Rate (%)','TIER':'Tier'})
        fig9.update_traces(texttemplate='%{text}%', textposition='outside')
        fig9.update_layout(height=300, margin=dict(t=10,b=10,l=10,r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig9, use_container_width=True)

    st.markdown('<div class="sec">Lead Time Distribution by Industry</div>', unsafe_allow_html=True)
    fig10 = px.box(filt_perf, x='INDUSTRY', y='LEAD_TIME_DAYS', color='INDUSTRY',
                   color_discrete_map=IND_COLORS, labels={'LEAD_TIME_DAYS':'Lead Time (Days)','INDUSTRY':''})
    fig10.update_layout(height=300, margin=dict(t=10,b=10,l=10,r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
    st.plotly_chart(fig10, use_container_width=True)

    st.markdown('<div class="sec">Supplier Scorecard</div>', unsafe_allow_html=True)
    sup_score = filt_perf.groupby('SUPPLIER_ID').agg(
        avg_otd=('ON_TIME_DELIVERY','mean'), avg_defect=('DEFECT_RATE','mean'),
        avg_lead=('LEAD_TIME_DAYS','mean'), total_spend=('SPEND','sum'), score=('SCORE','mean')
    ).reset_index().merge(filt_sup[['SUPPLIER_ID','SUPPLIER_NAME','INDUSTRY','TIER','REGION','RISK_LEVEL']], on='SUPPLIER_ID')
    sup_score = sup_score.sort_values('score', ascending=False).head(50)
    disp = sup_score[['SUPPLIER_NAME','INDUSTRY','TIER','REGION','avg_otd','avg_defect','avg_lead','total_spend','score','RISK_LEVEL']].copy()
    disp['avg_otd'] = (disp['avg_otd']*100).round(1).astype(str)+'%'
    disp['avg_defect'] = (disp['avg_defect']*100).round(2).astype(str)+'%'
    disp['avg_lead'] = disp['avg_lead'].round(1)
    disp['total_spend'] = disp['total_spend'].apply(lambda x: f'${x/1e3:.0f}K')
    disp['score'] = disp['score'].round(1)
    disp.columns = ['Supplier','Industry','Tier','Region','OTD','Defect Rate','Avg Lead (d)','Spend','Score','Risk']
    st.dataframe(disp, use_container_width=True, height=360, hide_index=True)

with tab4:
    st.markdown('<div class="sec">12-Week Demand Forecast</div>', unsafe_allow_html=True)
    fcast_skus = forecast['SKU_ID'].unique()
    sku_names = {s: skus[skus['SKU_ID']==s]['SKU_NAME'].values[0] if len(skus[skus['SKU_ID']==s]) > 0 else s for s in fcast_skus}
    sel_sku = st.selectbox("Select SKU", fcast_skus, format_func=lambda x: sku_names.get(x,x))
    sku_fcast = forecast[forecast['SKU_ID'] == sel_sku].sort_values('FORECAST_DATE')
    sku_hist = inventory[inventory['SKU_ID'] == sel_sku].sort_values('WEEK_START').tail(26)

    fig11 = go.Figure()
    fig11.add_trace(go.Scatter(x=sku_hist['WEEK_START'], y=sku_hist['WEEKLY_DEMAND'],
                                mode='lines', name='Historical', line=dict(color='#2563eb',width=2)))
    fig11.add_trace(go.Scatter(x=sku_fcast['FORECAST_DATE'], y=sku_fcast['DEMAND_FORECAST'],
                                mode='lines+markers', name='Forecast', line=dict(color='#d97706',width=2.5,dash='dash'),
                                marker=dict(size=6)))
    fig11.add_trace(go.Scatter(
        x=pd.concat([sku_fcast['FORECAST_DATE'], sku_fcast['FORECAST_DATE'][::-1]]),
        y=pd.concat([sku_fcast['UPPER_BOUND'], sku_fcast['LOWER_BOUND'][::-1]]),
        fill='toself', fillcolor='rgba(217,119,6,0.1)', line=dict(color='rgba(0,0,0,0)'),
        name='Confidence Band', showlegend=True
    ))
    fig11.update_layout(height=380, margin=dict(t=20,b=10,l=10,r=10), plot_bgcolor='rgba(0,0,0,0)',
                         paper_bgcolor='rgba(0,0,0,0)', yaxis_title='Weekly Demand', xaxis_title='Week',
                         legend=dict(orientation='h', yanchor='bottom', y=1.02))
    st.plotly_chart(fig11, use_container_width=True)

    r1c1,r1c2 = st.columns(2)
    with r1c1:
        st.markdown('<div class="sec">Avg Forecast by Industry (Next 12 Weeks)</div>', unsafe_allow_html=True)
        fcast_ind = forecast.merge(skus[['SKU_ID','INDUSTRY']], on='SKU_ID', how='left').dropna(subset=['INDUSTRY'])
        fcast_ind_agg = fcast_ind.groupby('INDUSTRY')['DEMAND_FORECAST'].mean().reset_index() if not fcast_ind.empty else pd.DataFrame(columns=['INDUSTRY','DEMAND_FORECAST'])
        fig12 = px.bar(fcast_ind_agg.sort_values('DEMAND_FORECAST'), x='DEMAND_FORECAST', y='INDUSTRY',
                       orientation='h', color='INDUSTRY', color_discrete_map=IND_COLORS,
                       labels={'DEMAND_FORECAST':'Avg Weekly Demand Forecast','INDUSTRY':''})
        fig12.update_layout(height=280, margin=dict(t=10,b=10,l=10,r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig12, use_container_width=True)
    with r1c2:
        st.markdown('<div class="sec">Forecast Trend Direction</div>', unsafe_allow_html=True)
        trend_data = forecast.merge(skus[['SKU_ID','INDUSTRY']], on='SKU_ID', how='left').dropna(subset=['INDUSTRY']).groupby('INDUSTRY')['TREND'].mean().reset_index()
        trend_data['direction'] = trend_data['TREND'].apply(lambda x: '↑ Growing' if x > 0.1 else ('↓ Declining' if x < -0.1 else '→ Stable'))
        trend_data['color'] = trend_data['TREND'].apply(lambda x: '#16a34a' if x > 0.1 else ('#e11d48' if x < -0.1 else '#d97706'))
        fig13 = px.bar(trend_data, x='TREND', y='INDUSTRY', orientation='h',
                       color='INDUSTRY', color_discrete_map=IND_COLORS,
                       labels={'TREND':'Avg Weekly Trend (units)','INDUSTRY':''}, text='direction')
        fig13.update_traces(textposition='outside')
        fig13.update_layout(height=280, margin=dict(t=10,b=10,l=10,r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig13, use_container_width=True)

with tab5:
    st.markdown('<div class="sec">Supply Chain Risk Summary</div>', unsafe_allow_html=True)
    r1c1,r1c2,r1c3 = st.columns(3)
    high_risk_sups = len(filt_sup[filt_sup['RISK_LEVEL']=='High'])
    single_source = len(filt_sup[filt_sup['SINGLE_SOURCE']==1])
    latest_inv2 = inventory.sort_values('WEEK_START').groupby('SKU_ID').last().reset_index()
    critical_skus_at_risk = len(latest_inv2[latest_inv2['STOCK_LEVEL'] < latest_inv2['STOCK_LEVEL'].quantile(0.1)])
    with r1c1: st.markdown(f'<div class="metric-card red"><div class="metric-value">{high_risk_sups}</div><div class="metric-label">High Risk Suppliers</div></div>', unsafe_allow_html=True)
    with r1c2: st.markdown(f'<div class="metric-card amber"><div class="metric-value">{single_source}</div><div class="metric-label">Single-Source SKUs</div></div>', unsafe_allow_html=True)
    with r1c3: st.markdown(f'<div class="metric-card red"><div class="metric-value">{critical_skus_at_risk}</div><div class="metric-label">SKUs Below 10th Pctile Stock</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    r2c1,r2c2 = st.columns(2)
    with r2c1:
        st.markdown('<div class="sec">Supplier Risk Distribution</div>', unsafe_allow_html=True)
        risk_dist = filt_sup.groupby(['INDUSTRY','RISK_LEVEL']).size().reset_index(name='count')
        fig14 = px.bar(risk_dist, x='INDUSTRY', y='count', color='RISK_LEVEL',
                       color_discrete_map=RISK_COLORS, labels={'count':'Suppliers','RISK_LEVEL':'Risk Level'})
        fig14.update_layout(height=300, margin=dict(t=10,b=10,l=10,r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig14, use_container_width=True)
    with r2c2:
        st.markdown('<div class="sec">Spend Concentration by Supplier (Top 20)</div>', unsafe_allow_html=True)
        spend_conc = filt_perf.groupby('SUPPLIER_ID')['SPEND'].sum().reset_index()
        spend_conc = spend_conc.merge(filt_sup[['SUPPLIER_ID','SUPPLIER_NAME','INDUSTRY']], on='SUPPLIER_ID')
        top20 = spend_conc.nlargest(20,'SPEND')
        fig15 = px.bar(top20.sort_values('SPEND'), x='SPEND', y='SUPPLIER_NAME', orientation='h',
                       color='INDUSTRY', color_discrete_map=IND_COLORS,
                       labels={'SPEND':'Total Spend ($)','SUPPLIER_NAME':''})
        fig15.update_layout(height=300, margin=dict(t=10,b=10,l=10,r=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig15, use_container_width=True)

    st.markdown('<div class="sec">At-Risk SKUs — Low Stock + High Criticality</div>', unsafe_allow_html=True)
    at_risk = latest_inv2.merge(skus[['SKU_ID','SKU_NAME','CRITICALITY','REORDER_POINT','SAFETY_STOCK','PRIMARY_SUPPLIER','INDUSTRY']], on='SKU_ID')
    at_risk = at_risk[
        (at_risk['STOCK_LEVEL'] < at_risk['REORDER_POINT']) &
        (at_risk['CRITICALITY'].isin(['Critical','High']))
    ].sort_values('DAYS_OF_SUPPLY')
    if sel_ind != "All Industries":
        at_risk = at_risk[at_risk['INDUSTRY'] == sel_ind]
    disp_risk = at_risk[['SKU_NAME','INDUSTRY','CRITICALITY','STOCK_LEVEL','REORDER_POINT','DAYS_OF_SUPPLY','FILL_RATE']].head(40).copy()
    disp_risk['FILL_RATE'] = (disp_risk['FILL_RATE']*100).round(1).astype(str)+'%'
    disp_risk['DAYS_OF_SUPPLY'] = disp_risk['DAYS_OF_SUPPLY'].round(1)
    disp_risk.columns = ['SKU','Industry','Criticality','Stock','Reorder Point','Days of Supply','Fill Rate']
    st.dataframe(disp_risk, use_container_width=True, height=340, hide_index=True)

    st.markdown('<div class="sec">Single-Source Supplier Risk</div>', unsafe_allow_html=True)
    ss_sups = filt_sup[filt_sup['SINGLE_SOURCE']==1][['SUPPLIER_ID','SUPPLIER_NAME','INDUSTRY','REGION','TIER','RISK_LEVEL','ANNUAL_SPEND']].copy()
    ss_sups['ANNUAL_SPEND'] = ss_sups['ANNUAL_SPEND'].apply(lambda x: f'${x/1e3:.0f}K')
    ss_sups.columns = ['ID','Supplier','Industry','Region','Tier','Risk','Annual Spend']
    st.dataframe(ss_sups, use_container_width=True, height=280, hide_index=True)
