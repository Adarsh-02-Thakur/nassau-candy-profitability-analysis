import pandas as pd
from pathlib import Path


# ============================================================
# FILE PATHS
# ============================================================

INPUT_FILE = Path("data/raw/nassau_candy_sales.csv")
OUTPUT_FILE = Path("data/processed/nassau_candy_cleaned.csv")


# ============================================================
# DATA CLEANING FUNCTION
# ============================================================

def clean_data():

    print("=" * 70)
    print("NASSAU CANDY DISTRIBUTOR - DATA CLEANING")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. CHECK INPUT FILE
    # --------------------------------------------------------

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    # --------------------------------------------------------
    # 2. LOAD DATA
    # --------------------------------------------------------

    df = pd.read_csv(INPUT_FILE)

    print(f"Original rows    : {len(df):,}")
    print(f"Original columns : {len(df.columns)}")

    # --------------------------------------------------------
    # 3. STANDARDIZE COLUMN NAMES
    # --------------------------------------------------------

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace("/", "_", regex=False)
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )

    print("\nStandardized columns:")
    print(df.columns.tolist())

    # --------------------------------------------------------
    # 4. REMOVE DUPLICATE ROWS
    # --------------------------------------------------------

    duplicate_count = df.duplicated().sum()

    if duplicate_count > 0:

        print(
            f"\nDuplicate rows removed: "
            f"{duplicate_count:,}"
        )

        df = df.drop_duplicates()

    else:

        print("\nDuplicate rows removed: 0")

    # --------------------------------------------------------
    # 5. CONVERT DATE COLUMNS
    # --------------------------------------------------------

    if "order_date" in df.columns:

        df["order_date"] = pd.to_datetime(
            df["order_date"],
            format="%d-%m-%Y",
            errors="coerce"
        )

    if "ship_date" in df.columns:

        df["ship_date"] = pd.to_datetime(
            df["ship_date"],
            format="%d-%m-%Y",
            errors="coerce"
        )

    # --------------------------------------------------------
    # 6. CHECK INVALID DATES
    # --------------------------------------------------------

    if "order_date" in df.columns:

        invalid_order_dates = df["order_date"].isna().sum()

        print(
            f"Invalid order dates: "
            f"{invalid_order_dates:,}"
        )

    if "ship_date" in df.columns:

        invalid_ship_dates = df["ship_date"].isna().sum()

        print(
            f"Invalid ship dates : "
            f"{invalid_ship_dates:,}"
        )

    # --------------------------------------------------------
    # 7. CONVERT NUMERIC COLUMNS
    # --------------------------------------------------------

    numeric_columns = [
        "row_id",
        "customer_id",
        "sales",
        "units",
        "gross_profit",
        "cost"
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # 8. STANDARDIZE TEXT COLUMNS
    # --------------------------------------------------------

    text_columns = [
        "order_id",
        "ship_mode",
        "country_region",
        "city",
        "state_province",
        "division",
        "region",
        "product_id",
        "product_name"
    ]

    for column in text_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    # --------------------------------------------------------
    # 9. CHECK MISSING VALUES
    # --------------------------------------------------------

    print("\nMissing values after type conversion:")

    missing_values = df.isna().sum()

    print(
        missing_values[
            missing_values > 0
        ].to_string()
        if missing_values.sum() > 0
        else "No missing values"
    )

    # --------------------------------------------------------
    # 10. REMOVE INVALID SALES
    # --------------------------------------------------------

    if "sales" in df.columns:

        before = len(df)

        df = df[
            df["sales"].notna()
            & (df["sales"] > 0)
        ]

        removed = before - len(df)

        print(
            f"\nInvalid sales rows removed: "
            f"{removed:,}"
        )

    # --------------------------------------------------------
    # 11. REMOVE INVALID UNITS
    # --------------------------------------------------------

    if "units" in df.columns:

        before = len(df)

        df = df[
            df["units"].notna()
            & (df["units"] > 0)
        ]

        removed = before - len(df)

        print(
            f"Invalid unit rows removed: "
            f"{removed:,}"
        )

    # --------------------------------------------------------
    # 12. VALIDATE COST
    # --------------------------------------------------------

    if "cost" in df.columns:

        before = len(df)

        df = df[
            df["cost"].notna()
            & (df["cost"] >= 0)
        ]

        removed = before - len(df)

        print(
            f"Invalid cost rows removed: "
            f"{removed:,}"
        )

    # --------------------------------------------------------
    # 13. VALIDATE GROSS PROFIT
    # --------------------------------------------------------

    if "gross_profit" in df.columns:

        before = len(df)

        df = df[
            df["gross_profit"].notna()
        ]

        removed = before - len(df)

        print(
            f"Invalid gross profit rows removed: "
            f"{removed:,}"
        )

    # --------------------------------------------------------
    # 14. VALIDATE FINANCIAL RELATIONSHIP
    #
    # Gross Profit = Sales - Cost
    # --------------------------------------------------------

    if {
        "sales",
        "cost",
        "gross_profit"
    }.issubset(df.columns):

        df["calculated_gross_profit"] = (
            df["sales"] - df["cost"]
        )

        df["profit_difference"] = (
            df["gross_profit"]
            - df["calculated_gross_profit"]
        )

        mismatches = (
            df["profit_difference"]
            .abs() > 0.01
        ).sum()

        print(
            f"\nGross profit mismatches: "
            f"{mismatches:,}"
        )

        # The source dataset already passed this
        # validation, so these helper columns are
        # removed before saving.

        df = df.drop(
            columns=[
                "calculated_gross_profit",
                "profit_difference"
            ]
        )

    # --------------------------------------------------------
    # 15. CREATE PROFITABILITY METRICS
    # --------------------------------------------------------

    df["gross_margin_pct"] = (
        df["gross_profit"]
        / df["sales"]
        * 100
    )

    df["profit_per_unit"] = (
        df["gross_profit"]
        / df["units"]
    )

    df["cost_ratio_pct"] = (
        df["cost"]
        / df["sales"]
        * 100
    )

    # --------------------------------------------------------
    # 16. CREATE DATE ANALYSIS COLUMNS
    # --------------------------------------------------------

    if "order_date" in df.columns:

        df["year"] = (
            df["order_date"].dt.year
        )

        df["month"] = (
            df["order_date"].dt.month
        )

        df["month_name"] = (
            df["order_date"].dt.month_name()
        )

        df["quarter"] = (
            df["order_date"].dt.to_period("Q")
            .astype(str)
        )

        df["year_month"] = (
            df["order_date"].dt.to_period("M")
            .astype(str)
        )

    # --------------------------------------------------------
    # 17. SHIPPING TIME
    # --------------------------------------------------------

    if {
        "order_date",
        "ship_date"
    }.issubset(df.columns):

        df["shipping_days"] = (
            df["ship_date"]
            - df["order_date"]
        ).dt.days

    # --------------------------------------------------------
    # 18. REVENUE CONTRIBUTION
    # --------------------------------------------------------

    total_sales = df["sales"].sum()

    if total_sales != 0:

        df["revenue_contribution_pct"] = (
            df["sales"]
            / total_sales
            * 100
        )

    else:

        df["revenue_contribution_pct"] = 0

    # --------------------------------------------------------
    # 19. PROFIT CONTRIBUTION
    # --------------------------------------------------------

    total_profit = df["gross_profit"].sum()

    if total_profit != 0:

        df["profit_contribution_pct"] = (
            df["gross_profit"]
            / total_profit
            * 100
        )

    else:

        df["profit_contribution_pct"] = 0

    # --------------------------------------------------------
    # 20. SORT DATA
    # --------------------------------------------------------

    if "order_date" in df.columns:

        df = df.sort_values(
            "order_date"
        ).reset_index(drop=True)

    # --------------------------------------------------------
    # 21. CREATE OUTPUT DIRECTORY
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # 22. SAVE CLEANED DATA
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # 23. FINAL REPORT
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("DATA CLEANING COMPLETE")
    print("=" * 70)

    print(
        f"Final rows       : {len(df):,}"
    )

    print(
        f"Final columns    : {len(df.columns)}"
    )

    print(
        f"Total Sales      : ${df['sales'].sum():,.2f}"
    )

    print(
        f"Total Cost       : ${df['cost'].sum():,.2f}"
    )

    print(
        f"Gross Profit     : ${df['gross_profit'].sum():,.2f}"
    )

    print(
        f"Gross Margin     : "
        f"{df['gross_profit'].sum() / df['sales'].sum() * 100:.2f}%"
    )

    print(
        f"Total Units      : {df['units'].sum():,}"
    )

    print(
        f"Unique Products  : "
        f"{df['product_id'].nunique():,}"
    )

    print(
        f"Unique Divisions : "
        f"{df['division'].nunique():,}"
    )

    print(
        f"\nSaved to: {OUTPUT_FILE}"
    )

    print("=" * 70)

    return df


# ============================================================
# RUN SCRIPT
# ============================================================

if __name__ == "__main__":
    clean_data()