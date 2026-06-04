"""
filters.py
----------
Data loading, cleaning, preprocessing, and filter logic for
the NASA EONET Natural Events Dashboard.
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path


# ──────────────────────────────────────────────
# 1.  DATA LOADING & CACHING
# ──────────────────────────────────────────────

DATA_PATH = Path(__file__).parent / "data" / "NASA_EONET_Natural_Events.csv"


@st.cache_data(show_spinner="Loading dataset…")
def load_data() -> pd.DataFrame:
    """
    Load the NASA EONET CSV, perform all cleaning steps, and return
    a fully-processed DataFrame.

    Returns
    -------
    pd.DataFrame
        Cleaned, feature-enriched DataFrame.
    """
    df = pd.read_csv(DATA_PATH)
    df = clean_data(df)
    df = engineer_features(df)
    return df


# ──────────────────────────────────────────────
# 2.  CLEANING
# ──────────────────────────────────────────────

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform data cleaning:
      - Strip whitespace from string columns
      - Parse datetime columns
      - Fill / drop missing values
      - Coerce numeric columns

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    df = df.copy()

    # ── strip strings ────────────────────────
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    # ── datetime parsing ─────────────────────
    for col in ["start_date", "end_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
            df[col] = df[col].dt.tz_localize(None)   # naive datetime for simplicity

    # ── replace empty strings with NaN ──────
    df.replace({"": np.nan, "nan": np.nan, "None": np.nan}, inplace=True)

    # ── numeric coercion ─────────────────────
    for col in ["latitude", "longitude", "magnitude", "duration_days"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── drop rows with no start_date ─────────
    df.dropna(subset=["start_date"], inplace=True)

    # ── fill remaining NaN ───────────────────
    if "status" in df.columns:
        df["status"] = df["status"].fillna("unknown")
    if "category" in df.columns:
        df["category"] = df["category"].fillna("Unknown")
    if "source" in df.columns:
        df["source"] = df["source"].fillna("Unknown")

    df.reset_index(drop=True, inplace=True)
    return df


# ──────────────────────────────────────────────
# 3.  FEATURE ENGINEERING
# ──────────────────────────────────────────────

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive additional columns useful for analysis:
      - year, month, month_name, day_of_week, quarter
      - event_duration_days (computed from date diff where missing)
      - hemisphere_lat, hemisphere_lon

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    df = df.copy()

    df["year"]        = df["start_date"].dt.year
    df["month"]       = df["start_date"].dt.month
    df["month_name"]  = df["start_date"].dt.strftime("%b")
    df["day_of_week"] = df["start_date"].dt.day_name()
    df["quarter"]     = df["start_date"].dt.quarter

    # compute duration from dates when column is missing / NaN
    if "duration_days" not in df.columns:
        df["duration_days"] = np.nan
    mask = df["duration_days"].isna() & df["end_date"].notna()
    df.loc[mask, "duration_days"] = (
        (df.loc[mask, "end_date"] - df.loc[mask, "start_date"]).dt.total_seconds() / 86400
    ).round(1)

    # hemispheres
    if "latitude" in df.columns:
        df["hemisphere_lat"] = np.where(df["latitude"] >= 0, "Northern", "Southern")
    if "longitude" in df.columns:
        df["hemisphere_lon"] = np.where(df["longitude"] >= 0, "Eastern", "Western")

    return df


# ──────────────────────────────────────────────
# 4.  FILTER APPLICATION
# ──────────────────────────────────────────────

def apply_filters(
    df: pd.DataFrame,
    date_range: tuple,
    categories: list,
    statuses: list,
    sources: list,
    mag_range: tuple,
    search_text: str,
) -> pd.DataFrame:
    """
    Apply all sidebar filters to the DataFrame and return the
    filtered subset.

    Parameters
    ----------
    df          : pd.DataFrame  – cleaned DataFrame
    date_range  : (start, end) as datetime.date
    categories  : list of category strings (empty = all)
    statuses    : list of status strings   (empty = all)
    sources     : list of source strings   (empty = all)
    mag_range   : (min, max) floats for magnitude
    search_text : keyword search on title column

    Returns
    -------
    pd.DataFrame
    """
    filtered = df.copy()

    # date range
    if date_range and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        filtered = filtered[
            (filtered["start_date"] >= start) &
            (filtered["start_date"] <= end)
        ]

    # categories
    if categories:
        filtered = filtered[filtered["category"].isin(categories)]

    # statuses
    if statuses:
        filtered = filtered[filtered["status"].isin(statuses)]

    # sources
    if sources:
        filtered = filtered[filtered["source"].isin(sources)]

    # magnitude
    if "magnitude" in filtered.columns and mag_range:
        lo, hi = mag_range
        mag_mask = filtered["magnitude"].isna() | (
            (filtered["magnitude"] >= lo) & (filtered["magnitude"] <= hi)
        )
        filtered = filtered[mag_mask]

    # keyword search on title
    if search_text and search_text.strip():
        kw = search_text.strip().lower()
        filtered = filtered[filtered["title"].str.lower().str.contains(kw, na=False)]

    return filtered.reset_index(drop=True)


# ──────────────────────────────────────────────
# 5.  SIDEBAR RENDER (returns filter values)
# ──────────────────────────────────────────────

def render_sidebar(df: pd.DataFrame) -> dict:
    """
    Render all sidebar filter widgets and return a dict of
    selected values to be passed to apply_filters().

    Parameters
    ----------
    df : pd.DataFrame  – unfiltered clean data

    Returns
    -------
    dict with keys: date_range, categories, statuses, sources,
                    mag_range, search_text
    """
    st.sidebar.title("🛰️ Filter Controls")
    st.sidebar.markdown("---")

    # ── Date range ───────────────────────────
    min_d = df["start_date"].min().date()
    max_d = df["start_date"].max().date()
    st.sidebar.subheader("📅 Date Range")
    date_range = st.sidebar.date_input(
        "Select date range",
        value=(min_d, max_d),
        min_value=min_d,
        max_value=max_d,
        key="date_range",
    )
    if len(date_range) == 1:
        date_range = (date_range[0], max_d)

    # ── Category multi-select ────────────────
    st.sidebar.subheader("🌪️ Event Category")
    all_cats = sorted(df["category"].dropna().unique().tolist())
    categories = st.sidebar.multiselect(
        "Select categories (all if empty)",
        options=all_cats,
        default=[],
        key="categories",
    )

    # ── Status filter ────────────────────────
    st.sidebar.subheader("🔴 Event Status")
    all_statuses = sorted(df["status"].dropna().unique().tolist())
    statuses = st.sidebar.multiselect(
        "Select statuses",
        options=all_statuses,
        default=[],
        key="statuses",
    )

    # ── Source filter ────────────────────────
    st.sidebar.subheader("📡 Data Source")
    all_sources = sorted(df["source"].dropna().unique().tolist())
    sources = st.sidebar.multiselect(
        "Select sources",
        options=all_sources,
        default=[],
        key="sources",
    )

    # ── Magnitude slider ─────────────────────
    st.sidebar.subheader("📊 Magnitude Range")
    mag_min = float(df["magnitude"].min(skipna=True))
    mag_max = float(df["magnitude"].max(skipna=True))
    mag_range = st.sidebar.slider(
        "Magnitude range",
        min_value=mag_min,
        max_value=mag_max,
        value=(mag_min, mag_max),
        step=round((mag_max - mag_min) / 100, 2),
        key="mag_range",
    )

    # ── Keyword search ───────────────────────
    st.sidebar.subheader("🔍 Search Events")
    search_text = st.sidebar.text_input(
        "Search by event title keyword",
        value="",
        key="search_text",
    )

    # ── Reset button ─────────────────────────
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
        for key in ["date_range", "categories", "statuses", "sources",
                    "mag_range", "search_text"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    return dict(
        date_range=date_range,
        categories=categories,
        statuses=statuses,
        sources=sources,
        mag_range=mag_range,
        search_text=search_text,
    )
