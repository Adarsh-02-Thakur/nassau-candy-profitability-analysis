import pandas as pd


# ============================================================
# OVERALL KPI CALCULATIONS
# ============================================================

def calculate_kpis(df):
    """Calculate overall business KPIs."""

    total_sales = df["sales"].sum()
    total_cost = df["cost"].sum()
    total_profit = df["gross_profit"].sum()
    total_units = df["units"].sum()

    gross_margin = (
        total_profit / total_sales * 100
        if total_sales != 0
        else 0
    )

    profit_per_unit = (
        total_profit / total_units
        if total_units != 0
        else 0
    )

    cost_ratio = (
        total_cost / total_sales * 100
        if total_sales != 0
        else 0
    )

    return {
        "total_sales": total_sales,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "total_units": total_units,
        "gross_margin": gross_margin,
        "profit_per_unit": profit_per_unit,
        "cost_ratio": cost_ratio,
    }


# ============================================================
# PRODUCT METRICS
# ============================================================

def product_metrics(df):
    """Calculate product-level profitability metrics."""

    product = (
        df.groupby(
            ["product_id", "product_name"],
            as_index=False
        )
        .agg(
            sales=("sales", "sum"),
            units=("units", "sum"),
            cost=("cost", "sum"),
            gross_profit=("gross_profit", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique"),
        )
    )

    product["gross_margin_pct"] = (
        product["gross_profit"]
        / product["sales"]
        * 100
    )

    product["profit_per_unit"] = (
        product["gross_profit"]
        / product["units"]
    )

    product["cost_ratio_pct"] = (
        product["cost"]
        / product["sales"]
        * 100
    )

    total_sales = product["sales"].sum()
    total_profit = product["gross_profit"].sum()

    product["revenue_contribution_pct"] = (
        product["sales"]
        / total_sales
        * 100
        if total_sales != 0
        else 0
    )

    product["profit_contribution_pct"] = (
        product["gross_profit"]
        / total_profit
        * 100
        if total_profit != 0
        else 0
    )

    product["sales_per_unit"] = (
        product["sales"]
        / product["units"]
    )

    return (
        product
        .sort_values("gross_profit", ascending=False)
        .reset_index(drop=True)
    )


# ============================================================
# DIVISION METRICS
# ============================================================

def division_metrics(df):
    """Calculate profitability by division."""

    division = (
        df.groupby("division", as_index=False)
        .agg(
            sales=("sales", "sum"),
            cost=("cost", "sum"),
            gross_profit=("gross_profit", "sum"),
            units=("units", "sum"),
            products=("product_id", "nunique"),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique"),
        )
    )

    division["gross_margin_pct"] = (
        division["gross_profit"]
        / division["sales"]
        * 100
    )

    division["profit_per_unit"] = (
        division["gross_profit"]
        / division["units"]
    )

    division["cost_ratio_pct"] = (
        division["cost"]
        / division["sales"]
        * 100
    )

    total_sales = division["sales"].sum()
    total_profit = division["gross_profit"].sum()

    division["revenue_contribution_pct"] = (
        division["sales"]
        / total_sales
        * 100
        if total_sales != 0
        else 0
    )

    division["profit_contribution_pct"] = (
        division["gross_profit"]
        / total_profit
        * 100
        if total_profit != 0
        else 0
    )

    return (
        division
        .sort_values("gross_profit", ascending=False)
        .reset_index(drop=True)
    )


# ============================================================
# REGION METRICS
# ============================================================

def region_metrics(df):
    """Calculate profitability by region."""

    region = (
        df.groupby("region", as_index=False)
        .agg(
            sales=("sales", "sum"),
            cost=("cost", "sum"),
            gross_profit=("gross_profit", "sum"),
            units=("units", "sum"),
            products=("product_id", "nunique"),
        )
    )

    region["gross_margin_pct"] = (
        region["gross_profit"]
        / region["sales"]
        * 100
    )

    region["profit_per_unit"] = (
        region["gross_profit"]
        / region["units"]
    )

    region["cost_ratio_pct"] = (
        region["cost"]
        / region["sales"]
        * 100
    )

    total_sales = region["sales"].sum()
    total_profit = region["gross_profit"].sum()

    region["revenue_contribution_pct"] = (
        region["sales"]
        / total_sales
        * 100
        if total_sales != 0
        else 0
    )

    region["profit_contribution_pct"] = (
        region["gross_profit"]
        / total_profit
        * 100
        if total_profit != 0
        else 0
    )

    return (
        region
        .sort_values("gross_profit", ascending=False)
        .reset_index(drop=True)
    )


# ============================================================
# MONTHLY METRICS
# ============================================================

def monthly_metrics(df):
    """Calculate monthly sales and profitability."""

    monthly = (
        df.groupby("year_month", as_index=False)
        .agg(
            sales=("sales", "sum"),
            cost=("cost", "sum"),
            gross_profit=("gross_profit", "sum"),
            units=("units", "sum"),
        )
    )

    monthly["gross_margin_pct"] = (
        monthly["gross_profit"]
        / monthly["sales"]
        * 100
    )

    monthly["profit_per_unit"] = (
        monthly["gross_profit"]
        / monthly["units"]
    )

    return monthly.sort_values(
        "year_month"
    ).reset_index(drop=True)


# ============================================================
# MARGIN VOLATILITY
# ============================================================

def margin_volatility(df):
    """Measure margin variability by product."""

    result = (
        df.groupby(
            ["product_id", "product_name"]
        )["gross_margin_pct"]
        .agg(
            average_margin="mean",
            margin_std="std",
            minimum_margin="min",
            maximum_margin="max",
        )
        .reset_index()
    )

    result["margin_range"] = (
        result["maximum_margin"]
        - result["minimum_margin"]
    )

    return (
        result
        .sort_values(
            "margin_std",
            ascending=False
        )
        .reset_index(drop=True)
    )


# ============================================================
# COST VS MARGIN DIAGNOSTICS
# ============================================================

def cost_margin_diagnostics(df):
    """Create product-level cost and margin diagnostics."""

    product = product_metrics(df)

    product["margin_category"] = pd.cut(
        product["gross_margin_pct"],
        bins=[
            float("-inf"),
            20,
            40,
            60,
            80,
            float("inf"),
        ],
        labels=[
            "Critical",
            "Low",
            "Moderate",
            "High",
            "Very High",
        ],
    )

    product["cost_category"] = pd.cut(
        product["cost_ratio_pct"],
        bins=[
            float("-inf"),
            20,
            40,
            60,
            80,
            float("inf"),
        ],
        labels=[
            "Very Low",
            "Low",
            "Moderate",
            "High",
            "Very High",
        ],
    )

    return product


# ============================================================
# GENERATE ALL METRICS
# ============================================================

def generate_all_metrics(df):
    """Generate all major analytical tables."""

    return {
        "kpis": calculate_kpis(df),
        "products": product_metrics(df),
        "divisions": division_metrics(df),
        "regions": region_metrics(df),
        "monthly": monthly_metrics(df),
        "margin_volatility": margin_volatility(df),
        "cost_margin": cost_margin_diagnostics(df),
    }