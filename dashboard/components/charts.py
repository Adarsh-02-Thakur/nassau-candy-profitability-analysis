import pandas as pd
import plotly.express as px


# ============================================================
# SALES VS PROFIT BY PRODUCT
# ============================================================

def sales_profit_by_product(df):

    product = (
        df.groupby(
            "product_name",
            as_index=False
        )
        .agg(
            Sales=("sales", "sum"),
            Gross_Profit=("gross_profit", "sum"),
        )
        .sort_values(
            "Sales",
            ascending=False
        )
    )

    fig = px.bar(
        product,
        x="product_name",
        y=[
            "Sales",
            "Gross_Profit"
        ],
        barmode="group",
        title="Sales vs Gross Profit by Product",
    )

    fig.update_layout(
        xaxis_title="Product",
        yaxis_title="Amount ($)",
        xaxis_tickangle=-45,
        legend_title="Metric",
        height=550,
        margin=dict(
            l=40,
            r=40,
            t=70,
            b=130,
        ),
    )

    return fig


# ============================================================
# MONTHLY SALES & PROFIT
# ============================================================

def monthly_sales_profit(df):

    monthly = (
        df.groupby(
            "year_month",
            as_index=False
        )
        .agg(
            Sales=("sales", "sum"),
            Gross_Profit=("gross_profit", "sum"),
        )
        .sort_values(
            "year_month"
        )
    )

    fig = px.line(
        monthly,
        x="year_month",
        y=[
            "Sales",
            "Gross_Profit"
        ],
        markers=True,
        title="Monthly Sales and Gross Profit Trend",
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        height=450,
    )

    return fig


# ============================================================
# DIVISION PROFIT
# ============================================================

def division_profit_chart(df):

    division = (
        df.groupby(
            "division",
            as_index=False
        )
        .agg(
            Gross_Profit=("gross_profit", "sum")
        )
        .sort_values(
            "Gross_Profit",
            ascending=False
        )
    )

    fig = px.bar(
        division,
        x="division",
        y="Gross_Profit",
        title="Gross Profit by Division",
        text_auto=".2f",
    )

    fig.update_layout(
        xaxis_title="Division",
        yaxis_title="Gross Profit ($)",
        height=420,
    )

    return fig


# ============================================================
# REGION PROFIT
# ============================================================

def region_profit_chart(df):

    region = (
        df.groupby(
            "region",
            as_index=False
        )
        .agg(
            Gross_Profit=("gross_profit", "sum")
        )
        .sort_values(
            "Gross_Profit",
            ascending=False
        )
    )

    fig = px.bar(
        region,
        x="region",
        y="Gross_Profit",
        title="Gross Profit by Region",
        text_auto=".2f",
    )

    fig.update_layout(
        xaxis_title="Region",
        yaxis_title="Gross Profit ($)",
        height=420,
    )

    return fig


# ============================================================
# GROSS MARGIN BY PRODUCT
# ============================================================

def margin_by_product(df):

    product = (
        df.groupby(
            "product_name",
            as_index=False
        )
        .agg(
            Sales=("sales", "sum"),
            Gross_Profit=("gross_profit", "sum"),
        )
    )

    product["Gross_Margin"] = (
        product["Gross_Profit"]
        / product["Sales"]
        * 100
    )

    product = product.sort_values(
        "Gross_Margin",
        ascending=True
    )

    fig = px.bar(
        product,
        x="Gross_Margin",
        y="product_name",
        orientation="h",
        title="Gross Margin by Product",
        text_auto=".1f",
    )

    fig.update_layout(
        xaxis_title="Gross Margin (%)",
        yaxis_title="Product",
        height=600,
    )

    return fig