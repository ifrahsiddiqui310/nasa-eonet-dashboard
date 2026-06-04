"""
app.py
------
NASA EONET Natural Events Dashboard
Exploratory Data Analysis Project

Run:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

from filters import load_data, apply_filters, render_sidebar
import charts as ch

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="NASA EONET Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CUSTOM CSS  (dark theme, card styling)
# ──────────────────────────────────────────────

st.markdown("""
<style>
/* ─── Global ─── */
body, .stApp { background-color: #0e1117; color: #e0e0e0; }
section[data-testid="stSidebar"] { background-color: #13151f; border-right: 1px solid #2e3147; }

/* ─── KPI Cards ─── */
.kpi-grid  { display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 24px; }
.kpi-card  {
    background: linear-gradient(135deg, #1a1d27 0%, #1e2235 100%);
    border: 1px solid #2e3147;
    border-radius: 12px;
    padding: 18px 22px;
    flex: 1 1 160px;
    min-width: 150px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.4);
    transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-3px); }
.kpi-label { font-size: 11px; color: #8892b0; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.kpi-value { font-size: 24px; font-weight: 700; color: #4fc3f7; line-height: 1.1; }
.kpi-sub   { font-size: 11px; color: #8892b0; margin-top: 4px; }

/* ─── Section headers ─── */
.section-header {
    background: linear-gradient(90deg, #1a1d27, #0e1117);
    border-left: 4px solid #4fc3f7;
    padding: 10px 16px;
    border-radius: 4px;
    margin: 20px 0 12px 0;
    font-size: 16px;
    font-weight: 600;
    color: #e0e0e0;
}

/* ─── Insight boxes ─── */
.insight-box {
    background: #1a1d27;
    border: 1px solid #2e3147;
    border-left: 3px solid #66bb6a;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 13px;
    color: #b0bec5;
    margin-top: 8px;
}

/* ─── Filter count badge ─── */
.filter-badge {
    display: inline-block;
    background: #ef5350;
    color: white;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: 600;
}

/* ─── Chart wrappers ─── */
.chart-container {
    background: #1a1d27;
    border: 1px solid #2e3147;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 8px;
}

/* Hide Streamlit branding */
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# DATA LOAD
# ──────────────────────────────────────────────

df_raw = load_data()


# ──────────────────────────────────────────────
# SIDEBAR (filters)
# ──────────────────────────────────────────────

filter_vals = render_sidebar(df_raw)
df = apply_filters(df_raw, **filter_vals)


# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────

st.markdown("""
<div style="text-align:center; padding: 10px 0 4px 0;">
  <span style="font-size:38px;">🛰️</span>
  <h1 style="color:#4fc3f7; margin:4px 0 0 0; font-size:32px; font-weight:800; letter-spacing:1px;">
    NASA EONET Natural Events Dashboard
  </h1>
  <p style="color:#8892b0; font-size:14px; margin-top:6px;">
    Interactive analysis of global natural disaster events tracked by the
    Earth Observatory Natural Event Tracker (EONET)
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ──────────────────────────────────────────────
# FILTERED DATA NOTICE
# ──────────────────────────────────────────────

if len(df) < len(df_raw):
    pct = len(df) / len(df_raw) * 100
    st.info(
        f"🔍 Filters active — showing **{len(df):,}** of **{len(df_raw):,}** events "
        f"({pct:.1f}%)"
    )


# ──────────────────────────────────────────────
# KPI CARDS
# ──────────────────────────────────────────────

def compute_kpis(d: pd.DataFrame) -> dict:
    """Compute KPI metrics from filtered DataFrame."""
    if d.empty:
        return {}
    total     = len(d)
    n_cats    = d["category"].nunique()
    n_sources = d["source"].nunique()
    earliest  = d["start_date"].min().strftime("%d %b %Y")
    latest    = d["start_date"].max().strftime("%d %b %Y")
    years_span = max(d["year"].max() - d["year"].min(), 1)
    avg_yr    = round(total / years_span, 1)
    top_cat   = d["category"].value_counts().idxmax()
    active_yr = str(int(d["year"].value_counts().idxmax()))
    avg_dur   = round(d["duration_days"].mean(), 1) if d["duration_days"].notna().any() else "N/A"
    open_pct  = round(d[d["status"] == "open"].shape[0] / total * 100, 1)
    return dict(total=total, n_cats=n_cats, n_sources=n_sources,
                earliest=earliest, latest=latest, avg_yr=avg_yr,
                top_cat=top_cat, active_yr=active_yr, avg_dur=avg_dur, open_pct=open_pct)

kpis = compute_kpis(df)

if kpis:
    st.markdown('<div class="section-header">📊 Key Performance Indicators</div>', unsafe_allow_html=True)

    cards_html = f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Total Events</div>
        <div class="kpi-value">{kpis['total']:,}</div>
        <div class="kpi-sub">in filtered range</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Event Categories</div>
        <div class="kpi-value">{kpis['n_cats']}</div>
        <div class="kpi-sub">unique types</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Data Sources</div>
        <div class="kpi-value">{kpis['n_sources']}</div>
        <div class="kpi-sub">organisations</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Earliest Event</div>
        <div class="kpi-value" style="font-size:17px;">{kpis['earliest']}</div>
        <div class="kpi-sub">start of record</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Latest Event</div>
        <div class="kpi-value" style="font-size:17px;">{kpis['latest']}</div>
        <div class="kpi-sub">most recent</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Avg Events / Year</div>
        <div class="kpi-value">{kpis['avg_yr']}</div>
        <div class="kpi-sub">annualised rate</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Top Category</div>
        <div class="kpi-value" style="font-size:15px;">{kpis['top_cat']}</div>
        <div class="kpi-sub">most frequent</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Most Active Year</div>
        <div class="kpi-value">{kpis['active_yr']}</div>
        <div class="kpi-sub">peak year</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Avg Duration</div>
        <div class="kpi-value">{kpis['avg_dur']} days</div>
        <div class="kpi-sub">closed events</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Open Events</div>
        <div class="kpi-value">{kpis['open_pct']}%</div>
        <div class="kpi-sub">currently active</div>
      </div>
    </div>
    """
    st.markdown(cards_html, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# DATASET PREVIEW
# ──────────────────────────────────────────────

with st.expander("📋 Cleaned Dataset Preview", expanded=False):
    st.dataframe(
        df.head(200).style.set_properties(**{
            "background-color": "#1a1d27",
            "color": "#e0e0e0",
        }),
        use_container_width=True,
        height=300,
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", f"{df.shape[0]:,}")
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing Values", f"{df.isnull().sum().sum():,}")


# ──────────────────────────────────────────────
# CHARTS  –  Section 1: Distribution
# ──────────────────────────────────────────────

st.markdown('<div class="section-header">🥧 Distribution Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1.3, 1])

with col1:
    st.markdown("**Event Category Distribution**")
    if not df.empty:
        st.pyplot(ch.pie_chart(df), use_container_width=True)
        st.markdown(
            f'<div class="insight-box">💡 <b>{df["category"].value_counts().idxmax()}</b> is the most '
            f'common category, accounting for '
            f'{df["category"].value_counts().iloc[0]/len(df)*100:.1f}% of all events.</div>',
            unsafe_allow_html=True,
        )

with col2:
    st.markdown("**Event Status Breakdown**")
    if not df.empty:
        st.pyplot(ch.status_pie(df), use_container_width=True)
        open_n = df[df["status"] == "open"].shape[0]
        st.markdown(
            f'<div class="insight-box">💡 <b>{open_n:,}</b> events are currently open / ongoing.</div>',
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────
# CHARTS – Section 2: Temporal Trends
# ──────────────────────────────────────────────

st.markdown('<div class="section-header">📈 Temporal Trends</div>', unsafe_allow_html=True)

st.markdown("**Monthly Event Trend Over Time**")
if not df.empty:
    st.pyplot(ch.line_chart_trend(df), use_container_width=True)
    peak_year = int(df["year"].value_counts().idxmax())
    st.markdown(
        f'<div class="insight-box">💡 The peak activity year is <b>{peak_year}</b>. '
        f'The dashed line shows the 6-month rolling average, smoothing seasonal spikes.</div>',
        unsafe_allow_html=True,
    )

st.markdown("**Year-over-Year Event Count**")
if not df.empty:
    st.pyplot(ch.yoy_bar_chart(df), use_container_width=True)

st.markdown("**Cumulative Annual Events by Category (Stacked Area)**")
if not df.empty:
    st.pyplot(ch.area_chart_cumulative(df), use_container_width=True)
    st.markdown(
        '<div class="insight-box">💡 Stacked area chart reveals which categories '
        'dominate event counts each year and how their shares shift over time.</div>',
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
# CHARTS – Section 3: Frequency & Counts
# ──────────────────────────────────────────────

st.markdown('<div class="section-header">📊 Frequency & Category Counts</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Top Event Categories (Bar Chart)**")
    if not df.empty:
        st.pyplot(ch.bar_chart_categories(df), use_container_width=True)

with col2:
    st.markdown("**Event Count Plot by Category**")
    if not df.empty:
        st.pyplot(ch.count_plot_category(df), use_container_width=True)

st.markdown('<div class="insight-box">💡 Severe Storms and Wildfires consistently '
            'lead event counts globally — reflecting their wide geographic spread.</div>',
            unsafe_allow_html=True)


# ──────────────────────────────────────────────
# CHARTS – Section 4: Duration Analysis
# ──────────────────────────────────────────────

st.markdown('<div class="section-header">⏱️ Event Duration Analysis</div>', unsafe_allow_html=True)

st.markdown("**Histogram: Distribution of Event Durations**")
if not df.empty:
    st.pyplot(ch.histogram_duration(df), use_container_width=True)
    if df["duration_days"].notna().any():
        med = df["duration_days"].median()
        p95 = df["duration_days"].quantile(0.95)
        st.markdown(
            f'<div class="insight-box">💡 Median event duration is <b>{med:.1f} days</b>. '
            f'95% of events last fewer than <b>{p95:.1f} days</b>.</div>',
            unsafe_allow_html=True,
        )

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Box Plot: Duration by Category**")
    if not df.empty:
        st.pyplot(ch.box_plot_duration(df), use_container_width=True)

with col2:
    st.markdown("**Violin Plot: Duration Probability Density**")
    if not df.empty:
        st.pyplot(ch.violin_plot_duration(df), use_container_width=True)

st.markdown('<div class="insight-box">💡 Box and violin plots together reveal both '
            'the spread and the probability density of duration, highlighting categories '
            'with heavy tails (long-lasting outlier events).</div>',
            unsafe_allow_html=True)


# ──────────────────────────────────────────────
# CHARTS – Section 5: Relationships
# ──────────────────────────────────────────────

st.markdown('<div class="section-header">🔗 Relationship & Correlation Analysis</div>',
            unsafe_allow_html=True)

col1, col2 = st.columns([1.3, 1])

with col1:
    st.markdown("**Scatter Plot: Magnitude vs. Duration**")
    if not df.empty:
        st.pyplot(ch.scatter_mag_duration(df), use_container_width=True)
        st.markdown(
            '<div class="insight-box">💡 Each dot is an event. '
            'Colour indicates category. Clusters reveal which categories '
            'tend to be high-magnitude and long-lasting.</div>',
            unsafe_allow_html=True,
        )

with col2:
    st.markdown("**Correlation Heatmap**")
    if not df.empty:
        st.pyplot(ch.heatmap_correlation(df), use_container_width=True)
        st.markdown(
            '<div class="insight-box">💡 Warm colours = positive correlation; '
            'cool colours = negative. Strong correlations guide feature selection '
            'for predictive modelling.</div>',
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────
# BONUS CHARTS
# ──────────────────────────────────────────────

st.markdown('<div class="section-header">🌟 Bonus Visualisations</div>', unsafe_allow_html=True)

st.markdown("**Bubble Chart: Event Frequency by Year & Category**")
if not df.empty:
    st.pyplot(ch.bubble_chart(df), use_container_width=True)
    st.markdown(
        '<div class="insight-box">💡 Bubble size encodes event count. '
        'Larger bubbles in later years suggest increased monitoring coverage '
        'or genuine uptick in event frequency.</div>',
        unsafe_allow_html=True,
    )

with st.expander("🔍 Pair Plot – Numerical Feature Relationships (may be slow for large datasets)"):
    if st.button("Generate Pair Plot"):
        with st.spinner("Rendering pair plot…"):
            if len(df) > 10:
                st.pyplot(ch.pair_plot(df), use_container_width=True)
            else:
                st.warning("Not enough data points for a pair plot.")


# ──────────────────────────────────────────────
# MAP  (basic lat/lon scatter via st.map)
# ──────────────────────────────────────────────

st.markdown('<div class="section-header">🗺️ Geographic Event Map</div>', unsafe_allow_html=True)

map_data = df.dropna(subset=["latitude", "longitude"])[["latitude", "longitude"]]
if not map_data.empty:
    st.map(map_data, zoom=1, use_container_width=True)
    st.markdown(
        f'<div class="insight-box">💡 Showing <b>{len(map_data):,}</b> events with valid '
        f'coordinates. Denser clusters indicate higher-risk geographic zones.</div>',
        unsafe_allow_html=True,
    )
else:
    st.info("No coordinate data available for the current filter selection.")


# ──────────────────────────────────────────────
# DATA SUMMARY TABLE
# ──────────────────────────────────────────────

st.markdown('<div class="section-header">📐 Statistical Summary</div>', unsafe_allow_html=True)

num_summary = df.select_dtypes(include=np.number).describe().T.round(3)
st.dataframe(num_summary, use_container_width=True)


# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#8892b0; font-size:12px; padding:10px 0 20px 0;">
  🛰️ <b>NASA EONET Natural Events Dashboard</b> &nbsp;|&nbsp;
  Built with Streamlit, Pandas, Matplotlib & Seaborn &nbsp;|&nbsp;
  Data: NASA Earth Observatory Natural Event Tracker
</div>
""", unsafe_allow_html=True)
