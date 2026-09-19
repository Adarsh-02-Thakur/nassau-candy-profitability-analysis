import pandas as pd


# ============================================================
# PRODUCT PROFITABILITY SEGMENTATION
# ============================================================

def classify_products(product_df):
    """
    Classify products using median sales and median gross margin.

    Categories:
        High Sales - High Margin
        High Sales - Low Margin
        Low Sales - High Margin
        Low Sales - Low Margin
    """

    result = product_df.copy()

    sales_median = result["sales"].median()
    margin_median = result["gross_margin_pct"].median()

    def classify(row):
        high_sales = row["sales"] >= sales_median
        high_margin = row["gross_margin_pct"] >= margin_median

        if high_sales and high_margin:
            return "High Sales - High Margin"

        if high_sales and not high_margin:
            return "High Sales - Low Margin"

        if not high_sales and high_margin:
            return "Low Sales - High Margin"

        return "Low Sales - Low Margin"

    result["profitability_segment"] = result.apply(
        classify,
        axis=1
    )

    return result


# ============================================================
# MARGIN RISK
# ============================================================

def add_margin_risk(product_df, threshold=20):
    """
    Add margin-risk classification.

    Margin < 10%      -> Critical
    Margin < threshold -> High
    Margin < 30%      -> Medium
    Otherwise         -> Healthy
    """

    result = product_df.copy()

    def risk(margin):

        if margin < 10:
            return "Critical"

        elif margin < threshold:
            return "High"

        elif margin < 30:
            return "Medium"

        return "Healthy"

    result["margin_risk"] = result[
        "gross_margin_pct"
    ].apply(risk)

    return result


# ============================================================
# DIVISION ANALYSIS
# ============================================================

def division_analysis(df):
    """
    Calculate profitability metrics by division.
    """

    division = (
        df.groupby(
            "division",
            as_index=False
        )
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

    return division.sort_values(
        "gross_profit",
        ascending=False
    ).reset_index(drop=True)


# ============================================================
# PARETO ANALYSIS
# ============================================================

def pareto_analysis(df, metric="gross_profit"):
    """
    Perform product-level Pareto analysis.

    metric can be:
        sales
        gross_profit
        units
    """

    valid_metrics = {
        "sales",
        "gross_profit",
        "units"
    }

    if metric not in valid_metrics:
        raise ValueError(
            f"Invalid metric '{metric}'. "
            f"Choose from {sorted(valid_metrics)}"
        )

    product = (
        df.groupby(
            ["product_id", "product_name"],
            as_index=False
        )
        .agg(
            value=(metric, "sum")
        )
    )

    product = product.sort_values(
        "value",
        ascending=False
    ).reset_index(drop=True)

    total = product["value"].sum()

    if total == 0:
        product["cumulative_value"] = 0
        product["cumulative_percentage"] = 0
    else:
        product["cumulative_value"] = (
            product["value"].cumsum()
        )

        product["cumulative_percentage"] = (
            product["cumulative_value"]
            / total
            * 100
        )

    product["product_rank"] = (
        product.index + 1
    )

    product["product_percentage"] = (
        product["product_rank"]
        / len(product)
        * 100
    )

    product["within_80_percent"] = (
        product["cumulative_percentage"] <= 80
    )

    # Include the first product that crosses 80%.
    crossing_80 = (
        product["cumulative_percentage"] >= 80
    )

    if crossing_80.any():

        first_crossing = crossing_80.idxmax()

        product.loc[
            :first_crossing,
            "within_80_percent"
        ] = True

    return product


# ============================================================
# PARETO SUMMARY
# ============================================================

def pareto_summary(df, metric="gross_profit"):
    """
    Return a concise Pareto summary.
    """

    pareto = pareto_analysis(
        df,
        metric=metric
    )

    if pareto.empty:
        return {
            "metric": metric,
            "total_value": 0,
            "products": 0,
            "products_for_80_percent": 0,
            "percentage_of_products": 0,
        }

    crossing = pareto[
        pareto["cumulative_percentage"] >= 80
    ]

    if crossing.empty:
        products_for_80 = len(pareto)
    else:
        products_for_80 = (
            crossing.index[0] + 1
        )

    total_products = len(pareto)

    percentage_products = (
        products_for_80
        / total_products
        * 100
    )

    return {
        "metric": metric,
        "total_value": pareto["value"].sum(),
        "products": total_products,
        "products_for_80_percent": products_for_80,
        "percentage_of_products": percentage_products,
    }


# ============================================================
# COMPLETE PROFITABILITY ANALYSIS
# ============================================================

def complete_profitability_analysis(df):
    """
    Generate all major profitability analysis tables.
    """

    from src.metrics import product_metrics

    products = product_metrics(df)

    products = classify_products(
        products
    )

    products = add_margin_risk(
        products
    )

    return {
        "products": products,
        "divisions": division_analysis(df),
        "pareto_sales": pareto_analysis(
            df,
            metric="sales"
        ),
        "pareto_profit": pareto_analysis(
            df,
            metric="gross_profit"
        ),
        "pareto_units": pareto_analysis(
            df,
            metric="units"
        ),
        "pareto_sales_summary": pareto_summary(
            df,
            metric="sales"
        ),
        "pareto_profit_summary": pareto_summary(
            df,
            metric="gross_profit"
        ),
    }