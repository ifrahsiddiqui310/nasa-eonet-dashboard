"""
charts.py
---------
All Matplotlib / Seaborn chart functions for the NASA EONET dashboard.
Each function accepts a filtered DataFrame and returns a Matplotlib Figure.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from typing import Optional

# ──────────────────────────────────────────────
# GLOBAL STYLE
# ──────────────────────────────────────────────

PALETTE      = "tab10"
BG_COLOR     = "#0e1117"
AXES_COLOR   = "#1a1d27"
TEXT_COLOR   = "#e0e0e0"
GRID_COLOR   = "#2e3147"
ACCENT_COLORS = [
    "#4fc3f7", "#ef5350", "#66bb6a", "#ffa726",
    "#ab47bc", "#26c6da", "#d4e157", "#ff7043",
    "#78909c", "#ec407a",
]

def _apply_dark_style(fig: plt.Figure, ax) -> None:
    """Apply consistent dark theme to a figure/axes pair."""
    fig.patch.set_facecolor(BG_COLOR)
    axes = [ax] if not hasattr(ax, "__len__") else ax.flatten()
    for a in axes:
        a.set_facecolor(AXES_COLOR)
        a.tick_params(colors=TEXT_COLOR, labelsize=9)
        a.xaxis.label.set_color(TEXT_COLOR)
        a.yaxis.label.set_color(TEXT_COLOR)
        a.title.set_color(TEXT_COLOR)
        for spine in a.spines.values():
            spine.set_edgecolor(GRID_COLOR)
        a.grid(color=GRID_COLOR, linestyle="--", linewidth=0.5, alpha=0.6)


def _new_fig(w=10, h=5):
    return plt.subplots(figsize=(w, h))


# ──────────────────────────────────────────────
# 1.  PIE CHART – Category distribution
# ──────────────────────────────────────────────

def pie_chart(df: pd.DataFrame) -> plt.Figure:
    """Pie chart showing proportional distribution of event categories."""
    counts = df["category"].value_counts()
    fig, ax = _new_fig(8, 6)
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=ACCENT_COLORS[: len(counts)],
        startangle=140,
        wedgeprops=dict(edgecolor=BG_COLOR, linewidth=1.5),
        pctdistance=0.82,
    )
    for t in texts:
        t.set_color(TEXT_COLOR)
        t.set_fontsize(9)
    for at in autotexts:
        at.set_color("#ffffff")
        at.set_fontsize(8)
    ax.set_title("Distribution of Natural Event Categories", fontsize=14,
                 color=TEXT_COLOR, pad=15)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    return fig


# ──────────────────────────────────────────────
# 2.  HISTOGRAM – Duration distribution
# ──────────────────────────────────────────────

def histogram_duration(df: pd.DataFrame) -> plt.Figure:
    """Histogram of event duration in days."""
    data = df["duration_days"].dropna()
    if data.empty:
        fig, ax = _new_fig()
        ax.text(0.5, 0.5, "No duration data available",
                ha="center", va="center", color=TEXT_COLOR, fontsize=12)
        _apply_dark_style(fig, ax)
        return fig

    fig, ax = _new_fig()
    n, bins, patches = ax.hist(data, bins=40, color=ACCENT_COLORS[0],
                                edgecolor=BG_COLOR, linewidth=0.5, alpha=0.85)
    # colour-grade bars by height
    max_n = n.max()
    for patch, count in zip(patches, n):
        patch.set_facecolor(plt.cm.plasma(count / max_n * 0.85 + 0.1))

    ax.set_xlabel("Duration (days)", color=TEXT_COLOR)
    ax.set_ylabel("Frequency", color=TEXT_COLOR)
    ax.set_title("Frequency Distribution of Event Durations", fontsize=13, color=TEXT_COLOR)
    median_val = data.median()
    ax.axvline(median_val, color="#ffa726", linewidth=1.8, linestyle="--",
               label=f"Median: {median_val:.1f} days")
    ax.legend(facecolor=AXES_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    _apply_dark_style(fig, ax)
    return fig


# ──────────────────────────────────────────────
# 3.  LINE CHART – Events trend over time
# ──────────────────────────────────────────────

def line_chart_trend(df: pd.DataFrame) -> plt.Figure:
    """Monthly event counts as a line chart."""
    if df.empty:
        fig, ax = _new_fig(); _apply_dark_style(fig, ax); return fig

    ts = (df.set_index("start_date")
            .resample("ME")["id"]
            .count()
            .reset_index(name="count"))
    ts.columns = ["date", "count"]

    fig, ax = _new_fig(12, 5)
    ax.plot(ts["date"], ts["count"], color=ACCENT_COLORS[0],
            linewidth=1.6, alpha=0.9, zorder=3)
    ax.fill_between(ts["date"], ts["count"],
                    color=ACCENT_COLORS[0], alpha=0.18)
    # 6-month rolling average
    ts["rolling"] = ts["count"].rolling(6, min_periods=1).mean()
    ax.plot(ts["date"], ts["rolling"], color=ACCENT_COLORS[2],
            linewidth=2, linestyle="--", label="6-month rolling avg", zorder=4)

    ax.set_xlabel("Date", color=TEXT_COLOR)
    ax.set_ylabel("Number of Events", color=TEXT_COLOR)
    ax.set_title("Natural Events Trend Over Time (Monthly)", fontsize=13, color=TEXT_COLOR)
    ax.legend(facecolor=AXES_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    _apply_dark_style(fig, ax)
    return fig


# ──────────────────────────────────────────────
# 4.  BAR CHART – Top event categories
# ──────────────────────────────────────────────

def bar_chart_categories(df: pd.DataFrame) -> plt.Figure:
    """Horizontal bar chart of event counts by category."""
    counts = df["category"].value_counts().head(12)
    fig, ax = _new_fig(10, 5)
    bars = ax.barh(counts.index[::-1], counts.values[::-1],
                   color=ACCENT_COLORS[: len(counts)], edgecolor=BG_COLOR,
                   linewidth=0.5, height=0.65)
    for bar, val in zip(bars, counts.values[::-1]):
        ax.text(bar.get_width() + max(counts.values) * 0.01, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", ha="left", color=TEXT_COLOR, fontsize=9)
    ax.set_xlabel("Number of Events", color=TEXT_COLOR)
    ax.set_title("Top Event Categories by Frequency", fontsize=13, color=TEXT_COLOR)
    ax.set_xlim(0, counts.max() * 1.12)
    _apply_dark_style(fig, ax)
    return fig


# ──────────────────────────────────────────────
# 5.  SCATTER PLOT – Magnitude vs Duration
# ──────────────────────────────────────────────

def scatter_mag_duration(df: pd.DataFrame) -> plt.Figure:
    """Scatter plot: magnitude vs. event duration coloured by category."""
    data = df.dropna(subset=["magnitude", "duration_days"])
    if len(data) < 5:
        fig, ax = _new_fig()
        ax.text(0.5, 0.5, "Insufficient data for scatter plot",
                ha="center", va="center", color=TEXT_COLOR, fontsize=12)
        _apply_dark_style(fig, ax)
        return fig

    cats = data["category"].unique()
    color_map = {c: ACCENT_COLORS[i % len(ACCENT_COLORS)] for i, c in enumerate(cats)}

    fig, ax = _new_fig(10, 6)
    for cat, grp in data.groupby("category"):
        ax.scatter(grp["magnitude"], grp["duration_days"],
                   label=cat, color=color_map[cat],
                   s=28, alpha=0.6, edgecolors="none")

    ax.set_xlabel("Magnitude", color=TEXT_COLOR)
    ax.set_ylabel("Duration (days)", color=TEXT_COLOR)
    ax.set_title("Event Magnitude vs. Duration by Category", fontsize=13, color=TEXT_COLOR)
    ax.legend(facecolor=AXES_COLOR, edgecolor=GRID_COLOR,
              labelcolor=TEXT_COLOR, fontsize=8,
              loc="upper right", ncol=2)
    _apply_dark_style(fig, ax)
    return fig


# ──────────────────────────────────────────────
# 6.  BOX PLOT – Duration by category
# ──────────────────────────────────────────────

def box_plot_duration(df: pd.DataFrame) -> plt.Figure:
    """Box plot of event duration (days) across categories."""
    data = df.dropna(subset=["duration_days"])
    if data.empty:
        fig, ax = _new_fig(); _apply_dark_style(fig, ax); return fig

    order = (data.groupby("category")["duration_days"]
             .median().sort_values(ascending=False).index.tolist())

    fig, ax = _new_fig(11, 6)
    sns.boxplot(
        data=data, x="category", y="duration_days", order=order,
        hue="category", palette=ACCENT_COLORS, legend=False, ax=ax,
        medianprops=dict(color="#ffffff", linewidth=2),
        boxprops=dict(edgecolor=BG_COLOR),
        whiskerprops=dict(color=TEXT_COLOR),
        capprops=dict(color=TEXT_COLOR),
        flierprops=dict(marker="o", markerfacecolor=ACCENT_COLORS[3],
                        markersize=3, alpha=0.5),
    )
    ax.set_xlabel("Category", color=TEXT_COLOR)
    ax.set_ylabel("Duration (days)", color=TEXT_COLOR)
    ax.set_title("Event Duration Distribution by Category", fontsize=13, color=TEXT_COLOR)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=9)
    _apply_dark_style(fig, ax)
    return fig


# ──────────────────────────────────────────────
# 7.  HEATMAP – Correlation matrix
# ──────────────────────────────────────────────

def heatmap_correlation(df: pd.DataFrame) -> plt.Figure:
    """Heatmap of Pearson correlation between numeric features."""
    num_df = df.select_dtypes(include=np.number).drop(
        columns=["month", "quarter"], errors="ignore")
    corr = num_df.corr()
    if corr.empty:
        fig, ax = _new_fig(); _apply_dark_style(fig, ax); return fig

    fig, ax = _new_fig(9, 7)
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(
        corr, ax=ax, mask=False,
        cmap="coolwarm", center=0,
        annot=True, fmt=".2f", annot_kws={"size": 8, "color": TEXT_COLOR},
        linewidths=0.5, linecolor=BG_COLOR,
        cbar_kws={"shrink": 0.75},
    )
    ax.set_title("Correlation Matrix of Numerical Features",
                 fontsize=13, color=TEXT_COLOR)
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right", fontsize=8)
    plt.setp(ax.get_yticklabels(), rotation=0, fontsize=8)
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.set_tick_params(color=TEXT_COLOR, labelcolor=TEXT_COLOR)
    _apply_dark_style(fig, ax)
    return fig


# ──────────────────────────────────────────────
# 8.  AREA CHART – Cumulative events over time
# ──────────────────────────────────────────────

def area_chart_cumulative(df: pd.DataFrame) -> plt.Figure:
    """Stacked area chart: cumulative events per year, split by top categories."""
    if df.empty:
        fig, ax = _new_fig(); _apply_dark_style(fig, ax); return fig

    top_cats = df["category"].value_counts().head(5).index.tolist()
    pivot = (df[df["category"].isin(top_cats)]
             .groupby(["year", "category"])["id"]
             .count()
             .unstack(fill_value=0))

    fig, ax = _new_fig(12, 5)
    pivot.plot.area(ax=ax, color=ACCENT_COLORS[: len(pivot.columns)],
                    alpha=0.75, linewidth=0)
    ax.set_xlabel("Year", color=TEXT_COLOR)
    ax.set_ylabel("Cumulative Events", color=TEXT_COLOR)
    ax.set_title("Yearly Event Trends by Top Categories (Stacked Area)", fontsize=13, color=TEXT_COLOR)
    ax.legend(title="Category", facecolor=AXES_COLOR, edgecolor=GRID_COLOR,
              labelcolor=TEXT_COLOR, title_fontsize=9, fontsize=8)
    _apply_dark_style(fig, ax)
    return fig


# ──────────────────────────────────────────────
# 9.  COUNT PLOT – Events by category
# ──────────────────────────────────────────────

def count_plot_category(df: pd.DataFrame) -> plt.Figure:
    """Count plot (bar chart variant) of event frequency per category."""
    fig, ax = _new_fig(11, 5)
    order = df["category"].value_counts().index.tolist()
    sns.countplot(data=df, x="category", order=order,
                  hue="category", palette=ACCENT_COLORS, legend=False, ax=ax,
                  edgecolor=BG_COLOR, linewidth=0.5)
    ax.set_xlabel("Category", color=TEXT_COLOR)
    ax.set_ylabel("Count", color=TEXT_COLOR)
    ax.set_title("Event Count by Category", fontsize=13, color=TEXT_COLOR)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=9)
    # add count labels
    for p in ax.patches:
        ax.annotate(str(int(p.get_height())),
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha="center", va="bottom", color=TEXT_COLOR, fontsize=8)
    _apply_dark_style(fig, ax)
    return fig


# ──────────────────────────────────────────────
# 10. VIOLIN PLOT – Duration distribution
# ──────────────────────────────────────────────

def violin_plot_duration(df: pd.DataFrame) -> plt.Figure:
    """Violin plot of event duration across categories."""
    data = df.dropna(subset=["duration_days"])
    if len(data) < 10:
        fig, ax = _new_fig(); _apply_dark_style(fig, ax); return fig

    order = (data.groupby("category")["duration_days"]
             .median().sort_values(ascending=False).index.tolist())

    fig, ax = _new_fig(11, 6)
    sns.violinplot(
        data=data, x="category", y="duration_days", order=order,
        hue="category", palette=ACCENT_COLORS, legend=False, ax=ax,
        inner="quartile",
        linewidth=0.8,
        cut=0,
    )
    ax.set_xlabel("Category", color=TEXT_COLOR)
    ax.set_ylabel("Duration (days)", color=TEXT_COLOR)
    ax.set_title("Probability Density of Event Duration by Category",
                 fontsize=13, color=TEXT_COLOR)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=9)
    _apply_dark_style(fig, ax)
    return fig


# ──────────────────────────────────────────────
# BONUS A.  BUBBLE CHART – Events per year
# ──────────────────────────────────────────────

def bubble_chart(df: pd.DataFrame) -> plt.Figure:
    """Bubble chart: year vs. category, bubble size = event count."""
    agg = (df.groupby(["year", "category"])["id"]
             .count()
             .reset_index(name="count"))
    if agg.empty:
        fig, ax = _new_fig(); _apply_dark_style(fig, ax); return fig

    cats = agg["category"].unique()
    cat_idx = {c: i for i, c in enumerate(sorted(cats))}
    colors = [ACCENT_COLORS[cat_idx[c] % len(ACCENT_COLORS)] for c in agg["category"]]

    fig, ax = _new_fig(13, 6)
    sc = ax.scatter(
        agg["year"],
        agg["category"],
        s=agg["count"] * 6,
        c=colors,
        alpha=0.65,
        edgecolors=BG_COLOR,
        linewidth=0.4,
    )
    ax.set_xlabel("Year", color=TEXT_COLOR)
    ax.set_ylabel("Category", color=TEXT_COLOR)
    ax.set_title("Bubble Chart: Event Frequency by Year & Category",
                 fontsize=13, color=TEXT_COLOR)
    # legend for bubble size
    for size_val in [10, 50, 100]:
        ax.scatter([], [], s=size_val * 6, c="#aaa", alpha=0.6,
                   label=f"{size_val} events")
    ax.legend(title="Count", facecolor=AXES_COLOR, edgecolor=GRID_COLOR,
              labelcolor=TEXT_COLOR, title_fontsize=9, fontsize=8)
    _apply_dark_style(fig, ax)
    return fig


# ──────────────────────────────────────────────
# BONUS B.  PAIR PLOT – Numerical features
# ──────────────────────────────────────────────

def pair_plot(df: pd.DataFrame) -> plt.Figure:
    """Pairplot of numeric columns coloured by event status."""
    cols = [c for c in ["magnitude", "duration_days", "latitude", "longitude"]
            if c in df.columns]
    data = df[cols + ["status"]].dropna()
    if len(data) < 20:
        fig, ax = _new_fig(); _apply_dark_style(fig, ax); return fig

    data = data.sample(min(500, len(data)), random_state=42)
    g = sns.pairplot(data, hue="status", vars=cols,
                     palette={"open": ACCENT_COLORS[0], "closed": ACCENT_COLORS[1]},
                     plot_kws=dict(alpha=0.45, s=14),
                     diag_kws=dict(fill=True, alpha=0.5))
    g.figure.patch.set_facecolor(BG_COLOR)
    for ax2 in g.axes.flatten():
        if ax2:
            ax2.set_facecolor(AXES_COLOR)
            ax2.tick_params(colors=TEXT_COLOR)
            for spine in ax2.spines.values():
                spine.set_edgecolor(GRID_COLOR)
    g.figure.suptitle("Pair Plot of Numerical Features by Status",
                       y=1.02, color=TEXT_COLOR, fontsize=13)
    return g.figure


# ──────────────────────────────────────────────
# BONUS C.  YEARLY BAR (YOY comparison)
# ──────────────────────────────────────────────

def yoy_bar_chart(df: pd.DataFrame) -> plt.Figure:
    """Year-over-year event count bar chart."""
    yearly = df.groupby("year")["id"].count().reset_index(name="count")
    fig, ax = _new_fig(13, 5)
    colors = [ACCENT_COLORS[i % len(ACCENT_COLORS)] for i in range(len(yearly))]
    ax.bar(yearly["year"].astype(str), yearly["count"],
           color=colors, edgecolor=BG_COLOR, linewidth=0.5, width=0.7)
    ax.set_xlabel("Year", color=TEXT_COLOR)
    ax.set_ylabel("Number of Events", color=TEXT_COLOR)
    ax.set_title("Year-over-Year Natural Event Count", fontsize=13, color=TEXT_COLOR)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
    _apply_dark_style(fig, ax)
    return fig


# ──────────────────────────────────────────────
# HELPER – status pie
# ──────────────────────────────────────────────

def status_pie(df: pd.DataFrame) -> plt.Figure:
    """Small pie chart for open vs closed status."""
    counts = df["status"].value_counts()
    fig, ax = _new_fig(5, 4)
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=[ACCENT_COLORS[2], ACCENT_COLORS[1]],
        startangle=90,
        wedgeprops=dict(edgecolor=BG_COLOR, linewidth=1.5),
    )
    for t in texts:
        t.set_color(TEXT_COLOR)
    for at in autotexts:
        at.set_color("#ffffff")
        at.set_fontsize(10)
    ax.set_title("Open vs Closed Events", fontsize=12, color=TEXT_COLOR)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    return fig
