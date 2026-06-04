# 🛰️ NASA EONET Natural Events Dashboard

**Course:** Exploratory Data Analysis  
**Instructor:** Ali Hassan Sherazi  
**Submission Date:** 05-June-2026  

---

## 📋 Project Overview

An interactive, professional-grade data visualization dashboard built with **Streamlit**,
analyzing the **NASA EONET (Earth Observatory Natural Event Tracker)** dataset.
The dashboard presents insights on global natural disaster events through 10+ chart types,
interactive filters, KPI summary cards, and a geographic event map.

---

## 🗂️ Project Structure

```
dashboard_project/
├── data/
│   └── NASA_EONET_Natural_Events.csv   ← dataset (do NOT rename)
├── notebooks/
│   └── analysis.ipynb                  ← EDA notebook
├── app.py                              ← main Streamlit dashboard
├── charts.py                           ← all chart / visualization functions
├── filters.py                          ← data loading, cleaning, filter logic
├── requirements.txt                    ← Python dependencies
└── README.md                           ← this file
```

---

## ⚙️ Installation & Setup

### 1. Clone / download the project
```bash
unzip dashboard_project.zip
cd dashboard_project
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the dashboard
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` in your default browser.

---

## 📊 Features

### KPI Summary Cards (10 metrics)
- Total Events, Event Categories, Data Sources
- Earliest / Latest Event Date
- Average Events per Year, Avg Duration
- Most Frequent Category, Most Active Year, % Open Events

### Interactive Filters (Sidebar)
| Filter | Type |
|--------|------|
| Date Range | Date picker |
| Event Category | Multi-select |
| Event Status | Multi-select |
| Data Source | Multi-select |
| Magnitude | Range slider |
| Keyword Search | Text input |
| Reset All | Button |

All charts update simultaneously when any filter changes.

### Visualizations (10 required + 3 bonus)
| # | Chart | Purpose |
|---|-------|---------|
| 1 | Pie Chart | Category distribution |
| 2 | Histogram | Duration frequency |
| 3 | Line Chart | Monthly trend + rolling avg |
| 4 | Bar Chart | Top categories |
| 5 | Scatter Plot | Magnitude vs Duration |
| 6 | Box Plot | Duration by category |
| 7 | Heatmap | Correlation matrix |
| 8 | Area Chart | Stacked yearly trends |
| 9 | Count Plot | Category frequencies |
| 10 | Violin Plot | Duration probability density |
| B1 | Bubble Chart | Year × Category × Count |
| B2 | Pair Plot | Numerical feature pairs |
| B3 | Geographic Map | Event locations (lat/lon) |

---

## 🔍 Key Insights

1. **Severe Storms** and **Wildfires** dominate event counts globally.
2. Most events have a short duration (< 10 days), but outliers extend to 90+ days.
3. Event reporting increased significantly after 2010, reflecting improved monitoring.
4. Earthquakes show the highest magnitude values; floods cover the largest areas.
5. Geographic clustering is visible in tropical belts and tectonically active zones.

---

## 🛠️ Technical Stack

| Tool | Role |
|------|------|
| Python 3.x | Core language |
| Pandas | Data loading, cleaning, filtering |
| NumPy | Numerical operations |
| Matplotlib | Chart creation |
| Seaborn | Statistical visualizations |
| Streamlit | Interactive dashboard framework |

---

## 📝 Notes

- Do **NOT** rename `NASA_EONET_Natural_Events.csv`.
- All charts use `@st.cache_data` for fast re-renders on filter changes.
- Dark theme applied globally via custom CSS injected in `app.py`.
