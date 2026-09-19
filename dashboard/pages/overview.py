import streamlit as st

from src.metrics import calculate_kpis

from dashboard.components.charts import (
    sales_profit_by_product,
    monthly_sales_profit,
    division_profit_chart,
    region_profit_chart,
    margin_by_product,
)


def show_overview(df):

    # ========================================================
    # HEADER
    # ========================================================

    st.title(
        "🍫 Product Line Profitability & Margin Performance"
    )

    st.write(
        "Nassau Candy Distributor • "
        "Executive Business Intelligence Dashboard"
    )

    st.divider()


    # ========================================================
    # EXECUTIVE OVERVIEW
    # ========================================================

    st.header("📊 Executive Overview")

    st.caption(
        "Monitor revenue, profitability, margins, "
        "product performance and regional performance."
    )


    # ========================================================
    # CALCULATE KPIs
    # ========================================================

    kpis = calculate_kpis(df)


    # ========================================================
    # KPI ROW 1
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            label="💰 Total Sales",
            value=f"${kpis['total_sales']:,.2f}",
        )


    with col2:

        st.metric(
            label="📈 Gross Profit",
            value=f"${kpis['total_profit']:,.2f}",
        )


    with col3:

        st.metric(
            label="🎯 Gross Margin",
            value=f"{kpis['gross_margin']:.2f}%",
        )


    with col4:

        st.metric(
            label="📦 Total Units",
            value=f"{kpis['total_units']:,}",
        )


    st.write("")


    # ========================================================
    # KPI ROW 2
    # ========================================================

    col5, col6, col7 = st.columns(3)


    with col5:

        st.metric(
            label="💵 Total Cost",
            value=f"${kpis['total_cost']:,.2f}",
        )


    with col6:

        st.metric(
            label="💎 Profit / Unit",
            value=f"${kpis['profit_per_unit']:.2f}",
        )


    with col7:

        st.metric(
            label="📊 Cost Ratio",
            value=f"{kpis['cost_ratio']:.2f}%",
        )


    st.divider()


    # ========================================================
    # MONTHLY TREND
    # ========================================================

    st.header("📈 Sales & Profit Trend")

    st.caption(
        "Monthly movement of sales and gross profit."
    )

    st.plotly_chart(
        monthly_sales_profit(df),
        use_container_width=True,
    )


    # ========================================================
    # PRODUCT PERFORMANCE
    # ========================================================

    st.header("🏆 Product Performance")

    st.caption(
        "Compare sales and gross profit across product lines."
    )

    st.plotly_chart(
        sales_profit_by_product(df),
        use_container_width=True,
    )


    # ========================================================
    # DIVISION + REGION
    # ========================================================

    st.header("🏢 Division & Regional Performance")

    col1, col2 = st.columns(2)


    with col1:

        st.plotly_chart(
            division_profit_chart(df),
            use_container_width=True,
        )


    with col2:

        st.plotly_chart(
            region_profit_chart(df),
            use_container_width=True,
        )


    # ========================================================
    # PRODUCT MARGIN
    # ========================================================

    st.header("🎯 Product Gross Margin")

    st.caption(
        "Gross margin percentage across individual products."
    )

    st.plotly_chart(
        margin_by_product(df),
        use_container_width=True,
    )


    # ========================================================
    # DATASET SUMMARY
    # ========================================================

    st.header("📋 Dataset Summary")


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Products",
            f"{df['product_id'].nunique():,}",
        )


    with col2:

        st.metric(
            "Divisions",
            f"{df['division'].nunique():,}",
        )


    with col3:

        st.metric(
            "Regions",
            f"{df['region'].nunique():,}",
        )


    with col4:

        st.metric(
            "Orders",
            f"{df['order_id'].nunique():,}",
        )


    # ========================================================
    # KEY BUSINESS INSIGHTS
    # ========================================================

    st.divider()

    st.header("💡 Key Business Indicators")


    product_summary = (
        df.groupby(
            "product_name",
            as_index=False
        )
        .agg(
            Sales=("sales", "sum"),
            Gross_Profit=("gross_profit", "sum"),
            Cost=("cost", "sum"),
            Units=("units", "sum"),
        )
    )


    product_summary["Gross_Margin"] = (
        product_summary["Gross_Profit"]
        / product_summary["Sales"]
        * 100
    )


    product_summary["Profit_Per_Unit"] = (
        product_summary["Gross_Profit"]
        / product_summary["Units"]
    )


    highest_profit_product = (
        product_summary
        .sort_values(
            "Gross_Profit",
            ascending=False
        )
        .iloc[0]
    )


    highest_margin_product = (
        product_summary
        .sort_values(
            "Gross_Margin",
            ascending=False
        )
        .iloc[0]
    )


    lowest_margin_product = (
        product_summary
        .sort_values(
            "Gross_Margin",
            ascending=True
        )
        .iloc[0]
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.info(
            f"🏆 **Highest Gross Profit**\n\n"
            f"{highest_profit_product['product_name']}\n\n"
            f"${highest_profit_product['Gross_Profit']:,.2f}"
        )


    with col2:

        st.success(
            f"📈 **Highest Gross Margin**\n\n"
            f"{highest_margin_product['product_name']}\n\n"
            f"{highest_margin_product['Gross_Margin']:.2f}%"
        )


    with col3:

        st.warning(
            f"⚠️ **Lowest Gross Margin**\n\n"
            f"{lowest_margin_product['product_name']}\n\n"
            f"{lowest_margin_product['Gross_Margin']:.2f}%"
        )


    # ========================================================
    # PRODUCT TABLE
    # ========================================================

    st.divider()

    st.header("📋 Product Profitability Table")

    display_df = product_summary.copy()

    display_df = display_df.sort_values(
        "Gross_Profit",
        ascending=False
    )


    display_df["Sales"] = display_df["Sales"].map(
        lambda x: f"${x:,.2f}"
    )

    display_df["Gross_Profit"] = display_df[
        "Gross_Profit"
    ].map(
        lambda x: f"${x:,.2f}"
    )

    display_df["Cost"] = display_df["Cost"].map(
        lambda x: f"${x:,.2f}"
    )

    display_df["Gross_Margin"] = display_df[
        "Gross_Margin"
    ].map(
        lambda x: f"{x:.2f}%"
    )

    display_df["Profit_Per_Unit"] = display_df[
        "Profit_Per_Unit"
    ].map(
        lambda x: f"${x:.2f}"
    )


    display_df = display_df.rename(
        columns={
            "product_name": "Product",
            "Sales": "Sales",
            "Gross_Profit": "Gross Profit",
            "Cost": "Cost",
            "Units": "Units",
            "Gross_Margin": "Gross Margin",
            "Profit_Per_Unit": "Profit / Unit",
        }
    )


    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )