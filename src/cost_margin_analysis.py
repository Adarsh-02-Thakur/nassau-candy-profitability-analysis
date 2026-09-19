import pandas as pd


# ============================================================
# COST VS MARGIN ANALYSIS
# ============================================================

def cost_margin_analysis(df):
    """
    Create product-level cost and margin diagnostics.
    """

    result = (
        df.groupby(
            ["product_id", "product_name"],
            as_index=False
        )
        .agg(
            sales=("sales", "sum"),
            cost=("cost", "sum"),
            gross_profit=("gross_profit", "sum"),
            units=("units", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique"),
        )
    )

    result["gross_margin_pct"] = (
        result["gross_profit"]
        / result["sales"]
        * 100
    )

    result["cost_ratio_pct"] = (
        result["cost"]
        / result["sales"]
        * 100
    )

    result["profit_per_unit"] = (
        result["gross_profit"]
        / result["units"]
    )

    result["sales_per_unit"] = (
        result["sales"]
        / result["units"]
    )

    return result.sort_values(
        "gross_margin_pct"
    ).reset_index(drop=True)


# ============================================================
# COST RISK CLASSIFICATION
# ============================================================

def classify_cost_risk(df):
    """
    Classify products according to cost ratio.
    """

    result = cost_margin_analysis(df)

    def classify(cost_ratio):

        if cost_ratio >= 80:
            return "Critical Cost"

        elif cost_ratio >= 60:
            return "High Cost"

        elif cost_ratio >= 40:
            return "Moderate Cost"

        return "Healthy Cost"

    result["cost_risk"] = result[
        "cost_ratio_pct"
    ].apply(classify)

    return result


# ============================================================
# MARGIN RISK CLASSIFICATION
# ============================================================

def classify_margin_risk(df):
    """
    Classify products according to gross margin.
    """

    result = cost_margin_analysis(df)

    def classify(margin):

        if margin < 10:
            return "Critical Margin"

        elif margin < 20:
            return "High Risk"

        elif margin < 40:
            return "Moderate Margin"

        return "Healthy Margin"

    result["margin_risk"] = result[
        "gross_margin_pct"
    ].apply(classify)

    return result


# ============================================================
# COST-MARGIN MATRIX
# ============================================================

def cost_margin_matrix(df):
    """
    Combine cost and margin risk into one diagnostic matrix.
    """

    result = cost_margin_analysis(df)

    def classify(row):

        cost_ratio = row["cost_ratio_pct"]
        margin = row["gross_margin_pct"]

        if cost_ratio >= 80 and margin < 20:
            return "Critical Cost / Margin"

        if cost_ratio >= 60 and margin < 40:
            return "High Cost / Low Margin"

        if cost_ratio >= 40 and margin < 40:
            return "Moderate Cost / Moderate Margin"

        if cost_ratio < 40 and margin >= 60:
            return "Low Cost / High Margin"

        if cost_ratio < 40 and margin >= 40:
            return "Low Cost / Healthy Margin"

        return "Other"

    result["diagnostic_category"] = result.apply(
        classify,
        axis=1
    )

    return result


# ============================================================
# HIGH-PRIORITY PRODUCTS
# ============================================================

def high_priority_products(df):
    """
    Identify products requiring closer profitability review.

    A product is considered high priority when:
      - gross margin is below 40%, OR
      - cost ratio is above 60%.
    """

    result = cost_margin_matrix(df)

    priority = result[
        (result["gross_margin_pct"] < 40)
        | (result["cost_ratio_pct"] > 60)
    ].copy()

    return priority.sort_values(
        ["gross_margin_pct", "cost_ratio_pct"],
        ascending=[True, False]
    ).reset_index(drop=True)


# ============================================================
# COST-MARGIN SUMMARY
# ============================================================

def cost_margin_summary(df):
    """
    Return summary statistics for cost and margin analysis.
    """

    result = cost_margin_analysis(df)

    total_sales = result["sales"].sum()
    total_cost = result["cost"].sum()
    total_profit = result["gross_profit"].sum()

    return {
        "total_sales": total_sales,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "overall_margin_pct": (
            total_profit / total_sales * 100
            if total_sales != 0
            else 0
        ),
        "average_product_margin_pct": (
            result["gross_margin_pct"].mean()
        ),
        "highest_margin_product": (
            result.loc[
                result["gross_margin_pct"].idxmax(),
                "product_name"
            ]
        ),
        "lowest_margin_product": (
            result.loc[
                result["gross_margin_pct"].idxmin(),
                "product_name"
            ]
        ),
        "highest_cost_ratio_product": (
            result.loc[
                result["cost_ratio_pct"].idxmax(),
                "product_name"
            ]
        ),
        "lowest_cost_ratio_product": (
            result.loc[
                result["cost_ratio_pct"].idxmin(),
                "product_name"
            ]
        ),
    }