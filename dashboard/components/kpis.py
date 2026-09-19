import streamlit as st


def display_kpis(kpis):

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "💰 Total Sales",
            f"${kpis['total_sales']:,.2f}"
        )

    with col2:

        st.metric(
            "📈 Gross Profit",
            f"${kpis['total_profit']:,.2f}"
        )

    with col3:

        st.metric(
            "🎯 Gross Margin",
            f"{kpis['gross_margin']:.2f}%"
        )

    with col4:

        st.metric(
            "📦 Total Units",
            f"{kpis['total_units']:,}"
        )


    col5, col6, col7 = st.columns(3)

    with col5:

        st.metric(
            "💵 Total Cost",
            f"${kpis['total_cost']:,.2f}"
        )

    with col6:

        st.metric(
            "💎 Profit / Unit",
            f"${kpis['profit_per_unit']:.2f}"
        )

    with col7:

        st.metric(
            "📊 Cost Ratio",
            f"{kpis['cost_ratio']:.2f}%"
        )