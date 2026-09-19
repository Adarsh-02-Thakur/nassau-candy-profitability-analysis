import sys
from pathlib import Path

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

import streamlit as st
import pandas as pd

from dashboard.pages.overview import show_overview


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Nassau Candy Profitability",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM STREAMLIT CSS
# IMPORTANT:
# This is CSS only. There is NO HTML CONTENT here.
# ============================================================

st.markdown(
    """
    <style>

    /* Main application background */
    .stApp {
        background-color: #f4f7fb;
    }

    /* Main content width */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: white !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.06);
    }

    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {
        color: #111827 !important;
        font-weight: 800 !important;
    }

    /* Charts */
    div[data-testid="stPlotlyChart"] {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 8px;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.05);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    /* Dataframes */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "nassau_candy_cleaned.csv"
)


@st.cache_data
def load_data():

    df = pd.read_csv(DATA_FILE)

    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )

    return df


df = load_data()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🍫 Nassau Candy")

st.sidebar.write(
    "Product Line Profitability & "
    "Margin Performance Analysis"
)

st.sidebar.divider()


# ============================================================
# DATE FILTER
# ============================================================

min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()

date_range = st.sidebar.date_input(
    "📅 Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)


# ============================================================
# DATE FILTER LOGIC
# ============================================================

filtered_df = df.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:

    start_date = pd.Timestamp(date_range[0])

    # Include the entire end date
    end_date = (
        pd.Timestamp(date_range[1])
        + pd.Timedelta(days=1)
    )

    filtered_df = filtered_df[
        (filtered_df["order_date"] >= start_date)
        & (filtered_df["order_date"] < end_date)
    ].copy()


# ============================================================
# DIVISION FILTER
# ============================================================

divisions = sorted(
    filtered_df["division"]
    .dropna()
    .unique()
    .tolist()
)

selected_divisions = st.sidebar.multiselect(
    "🏢 Division",
    divisions,
    default=divisions,
)


if selected_divisions:

    filtered_df = filtered_df[
        filtered_df["division"].isin(
            selected_divisions
        )
    ].copy()


# ============================================================
# REGION FILTER
# ============================================================

regions = sorted(
    filtered_df["region"]
    .dropna()
    .unique()
    .tolist()
)

selected_regions = st.sidebar.multiselect(
    "🌎 Region",
    regions,
    default=regions,
)


if selected_regions:

    filtered_df = filtered_df[
        filtered_df["region"].isin(
            selected_regions
        )
    ].copy()


# ============================================================
# PRODUCT SEARCH
# ============================================================

product_search = st.sidebar.text_input(
    "🔎 Search Product",
    placeholder="Type product name..."
)


if product_search:

    filtered_df = filtered_df[
        filtered_df["product_name"]
        .str.contains(
            product_search,
            case=False,
            na=False
        )
    ].copy()


# ============================================================
# MARGIN FILTER
# ============================================================

margin_threshold = st.sidebar.slider(
    "📊 Minimum Gross Margin (%)",
    min_value=0,
    max_value=100,
    value=0,
    step=5,
)


if margin_threshold > 0:

    product_sales = (
        filtered_df
        .groupby("product_id")["sales"]
        .sum()
    )

    product_profit = (
        filtered_df
        .groupby("product_id")["gross_profit"]
        .sum()
    )

    product_margin = (
        product_profit
        / product_sales
        * 100
    )

    valid_products = product_margin[
        product_margin >= margin_threshold
    ].index

    filtered_df = filtered_df[
        filtered_df["product_id"].isin(
            valid_products
        )
    ].copy()


# ============================================================
# SIDEBAR SUMMARY
# ============================================================

st.sidebar.divider()

st.sidebar.metric(
    "Filtered Rows",
    f"{len(filtered_df):,}"
)

st.sidebar.metric(
    "Products",
    f"{filtered_df['product_id'].nunique():,}"
)

st.sidebar.metric(
    "Divisions",
    f"{filtered_df['division'].nunique():,}"
)

st.sidebar.metric(
    "Regions",
    f"{filtered_df['region'].nunique():,}"
)


# ============================================================
# NAVIGATION
# ============================================================

st.sidebar.divider()

st.sidebar.subheader("📑 Dashboard")

page = st.sidebar.radio(
    "Select Page",
    [
        "Executive Overview",
    ],
)


# ============================================================
# MAIN APPLICATION
# ============================================================

if filtered_df.empty:

    st.warning(
        "⚠️ No data matches the selected filters."
    )

else:

    if page == "Executive Overview":

        show_overview(filtered_df)