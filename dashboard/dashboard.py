from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "train_prepared.parquet"
)

st.set_page_config(
    page_title="FreshRetail Inventory Dashboard",
    layout="wide"
)

@st.cache_data
def load_data():
    columns = [
        "city_id", "store_id", "product_id", "dt",
        "sale_amount", "HasStockout", "StockoutRate",
        "stock_hour6_22_cnt", "DiscountPercent",
        "WeekendFlag", "holiday_flag", "activity_flag"
    ]

    data = pd.read_parquet(DATA_PATH, columns=columns)
    data["dt"] = pd.to_datetime(data["dt"])
    return data

data = load_data()

page = st.sidebar.radio(
    "Dashboard page",
    [
        "Executive Overview",
        "Inventory Risk",
        "Decision Driver"
    ]
)

st.title(page)
st.caption(
    "FreshRetailNet — sales and inventory analysis. "
    "Sales are observed sales, not necessarily true demand."
)

if page == "Executive Overview":
    st.sidebar.subheader("Filters")

    min_date = data["dt"].min().date()
    max_date = data["dt"].max().date()

    selected_dates = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if not isinstance(selected_dates, tuple) or len(selected_dates) != 2:
        st.info("Hãy chọn cả ngày bắt đầu và ngày kết thúc.")
        st.stop()

    selected_city = st.sidebar.selectbox(
        "City",
        ["All"] + sorted(data["city_id"].unique().tolist())
    )

    start_date = pd.Timestamp(selected_dates[0])
    end_date = pd.Timestamp(selected_dates[1]) + pd.Timedelta(days=1)

    filtered = data[
        (data["dt"] >= start_date) &
        (data["dt"] < end_date)
    ]

    if selected_city != "All":
        filtered = filtered[filtered["city_id"] == selected_city]

    if filtered.empty:
        st.warning("Không có dữ liệu trong bộ lọc đã chọn.")
        st.stop()

    daily_sales = (
        filtered.groupby("dt", as_index=False)["sale_amount"]
        .sum()
        .rename(columns={"sale_amount": "TotalSales"})
    )

    stockout_rows = filtered[filtered["HasStockout"]]
    stockout_rate = 100 * filtered["HasStockout"].mean()
    avg_stockout_hours = (
        stockout_rows["stock_hour6_22_cnt"].mean()
        if not stockout_rows.empty
        else 0
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total observed sales", f'{filtered["sale_amount"].sum():,.1f}')
    k2.metric("Average sales per day", f'{daily_sales["TotalSales"].mean():,.1f}')
    k3.metric("Records with stockout", f"{stockout_rate:.2f}%")
    k4.metric("Avg. stockout duration", f"{avg_stockout_hours:.2f} hours")

    left, right = st.columns(2)

    with left:
        st.subheader("Daily sales trend")
        fig_trend = px.line(
            daily_sales,
            x="dt",
            y="TotalSales",
            markers=True,
            labels={"dt": "Date", "TotalSales": "Observed sales"},
            hover_data={"TotalSales": ":,.2f"}
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with right:
        if selected_city == "All":
            group_col = "city_id"
            chart_title = "Top 10 cities by observed sales"
        else:
            group_col = "store_id"
            chart_title = f"Top 10 stores in City {selected_city}"

        comparison = (
            filtered.groupby(group_col)
            .agg(
                TotalSales=("sale_amount", "sum"),
                AvgSales=("sale_amount", "mean"),
                Observations=("sale_amount", "size")
            )
            .reset_index()
            .nlargest(10, "TotalSales")
        )

        comparison["Entity"] = comparison[group_col].astype(str)

        st.subheader(chart_title)
        fig_comparison = px.bar(
            comparison,
            x="Entity",
            y="TotalSales",
            hover_data={
                "AvgSales": ":.3f",
                "Observations": True,
                "Entity": False
            },
            labels={
                "Entity": "City / Store ID",
                "TotalSales": "Observed sales"
            }
        )
        st.plotly_chart(fig_comparison, use_container_width=True)

    st.caption(
        "Decision cue: use the sales trend and city/store comparison to identify "
        "where inventory planning deserves attention. Total sales can reflect "
        "different numbers of observations; hover to compare average sales and coverage."
    )

elif page == "Inventory Risk":
    st.sidebar.subheader("Inventory Risk filters")

    min_date = data["dt"].min().date()
    max_date = data["dt"].max().date()

    selected_dates = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="risk_dates"
    )

    if not isinstance(selected_dates, tuple) or len(selected_dates) != 2:
        st.info("Hãy chọn cả ngày bắt đầu và ngày kết thúc.")
        st.stop()

    selected_city = st.sidebar.selectbox(
        "City",
        ["All"] + sorted(data["city_id"].unique().tolist()),
        key="risk_city"
    )

    start_date = pd.Timestamp(selected_dates[0])
    end_date = pd.Timestamp(selected_dates[1]) + pd.Timedelta(days=1)

    filtered = data[
        (data["dt"] >= start_date) &
        (data["dt"] < end_date)
    ]

    if selected_city != "All":
        filtered = filtered[filtered["city_id"] == selected_city]

    if filtered.empty:
        st.warning("Không có dữ liệu trong bộ lọc đã chọn.")
        st.stop()

    stockout_rows = filtered[filtered["HasStockout"]]

    stockout_rate = 100 * filtered["HasStockout"].mean()
    avg_duration = (
        stockout_rows["stock_hour6_22_cnt"].mean()
        if not stockout_rows.empty
        else 0
    )

    product_summary = (
        filtered.groupby("product_id")
        .agg(
            Records=("sale_amount", "size"),
            AvgSales=("sale_amount", "mean"),
            StockoutRatePct=("HasStockout", "mean"),
            StockoutDays=("HasStockout", "sum")
        )
        .reset_index()
    )
    product_summary["StockoutRatePct"] *= 100

    product_duration = (
        stockout_rows.groupby("product_id")["stock_hour6_22_cnt"]
        .mean()
        .rename("AvgStockoutHours")
    )
    product_summary = product_summary.merge(
        product_duration,
        on="product_id",
        how="left"
    )

    store_summary = (
        filtered.groupby(["city_id", "store_id"])
        .agg(
            Records=("sale_amount", "size"),
            AvgSales=("sale_amount", "mean"),
            StockoutRatePct=("HasStockout", "mean"),
            StockoutDays=("HasStockout", "sum")
        )
        .reset_index()
    )
    store_summary["StockoutRatePct"] *= 100

    store_duration = (
        stockout_rows.groupby(["city_id", "store_id"])["stock_hour6_22_cnt"]
        .mean()
        .rename("AvgStockoutHours")
        .reset_index()
    )
    store_summary = store_summary.merge(
        store_duration,
        on=["city_id", "store_id"],
        how="left"
    )

    k1, k2, k3 = st.columns(3)
    k1.metric("Records with stockout", f"{stockout_rate:.2f}%")
    k2.metric("Avg. duration on stockout records", f"{avg_duration:.2f} hours")

    sales_threshold = product_summary["AvgSales"].median()
    stockout_threshold = product_summary["StockoutRatePct"].median()

    product_summary["SalesLevel"] = product_summary["AvgSales"].ge(
        sales_threshold
    ).map({True: "High Sales", False: "Low Sales"})

    product_summary["StockoutLevel"] = product_summary["StockoutRatePct"].ge(
        stockout_threshold
    ).map({True: "High Stockout", False: "Low Stockout"})

    high_high = product_summary[
        (product_summary["SalesLevel"] == "High Sales") &
        (product_summary["StockoutLevel"] == "High Stockout") &
        (product_summary["Records"] >= 100)
    ].sort_values(
        ["StockoutRatePct", "AvgSales"],
        ascending=False
    )

    k3.metric("Priority products", len(high_high))

    st.subheader("Product sales vs. stockout risk")
    fig_risk = px.scatter(
        product_summary,
        x="AvgSales",
        y="StockoutRatePct",
        size="Records",
        color="SalesLevel",
        hover_name="product_id",
        hover_data={
            "StockoutLevel": True,
            "StockoutDays": True,
            "AvgStockoutHours": ":.2f",
            "Records": True
        },
        labels={
            "product_id": "Product ID",
            "AvgSales": "Average observed sales per record",
            "StockoutRatePct": "Records with stockout (%)",
            "SalesLevel": "Sales group"
        }
    )
    st.plotly_chart(fig_risk, use_container_width=True)

    left, right = st.columns(2)

    with left:
        st.subheader("Priority products: High Sales + High Stockout")
        st.caption(
            "Ưu tiên xem xét sản phẩm có doanh số trung bình và tỷ lệ hết hàng "
            "đều từ mức trung vị trở lên."
        )
        st.dataframe(
            high_high[
                [
                    "product_id", "AvgSales", "StockoutRatePct",
                    "AvgStockoutHours", "Records"
                ]
            ].head(10).round(2),
            use_container_width=True,
            hide_index=True
        )

    with right:
        st.subheader("Stores with frequent stockouts")
        st.caption("Các cửa hàng dưới đây có ít nhất 100 quan sát trong bộ lọc.")
        frequent_stores = (
            store_summary[store_summary["Records"] >= 100]
            .sort_values("StockoutRatePct", ascending=False)
            .head(10)
        )
        st.dataframe(
            frequent_stores[
                [
                    "city_id", "store_id", "AvgSales",
                    "StockoutRatePct", "AvgStockoutHours", "Records"
                ]
            ].round(2),
            use_container_width=True,
            hide_index=True
        )

    st.caption(
        f"Ngưỡng phân nhóm được tính theo trung vị trong dữ liệu đang lọc: "
        f"doanh số trung bình = {sales_threshold:.3f}; "
        f"tỷ lệ hết hàng = {stockout_threshold:.2f}%. "
        "Đây là cách xếp hạng tương đối, không phải ngưỡng tồn kho tối ưu. "
        "Doanh số quan sát có thể thấp hơn nhu cầu thực khi sản phẩm hết hàng."
    )

else:
    st.sidebar.subheader("Decision Driver filters")

    min_date = data["dt"].min().date()
    max_date = data["dt"].max().date()

    selected_dates = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="driver_dates"
    )

    if not isinstance(selected_dates, tuple) or len(selected_dates) != 2:
        st.info("Hãy chọn cả ngày bắt đầu và ngày kết thúc.")
        st.stop()

    all_cities = sorted(data["city_id"].unique().tolist())
    selected_cities = st.sidebar.multiselect(
        "Cities",
        all_cities,
        default=all_cities,
        key="driver_cities"
    )

    start_date = pd.Timestamp(selected_dates[0])
    end_date = pd.Timestamp(selected_dates[1]) + pd.Timedelta(days=1)

    filtered = data[
        (data["dt"] >= start_date) &
        (data["dt"] < end_date) &
        (data["city_id"].isin(selected_cities))
    ]

    if filtered.empty:
        st.warning("Không có dữ liệu trong bộ lọc đã chọn.")
        st.stop()

    # DiscountPercent có ý nghĩa trong khoảng 0–100%.
    valid_discount = filtered[
        filtered["DiscountPercent"].between(0, 100)
    ].copy()
    invalid_discount_count = len(filtered) - len(valid_discount)

    band_labels = [
        "No discount",
        "Low (0–10%)",
        "Medium (10–30%)",
        "High (>30%)"
    ]

    valid_discount["DiscountBand"] = pd.cut(
        valid_discount["DiscountPercent"],
        bins=[-0.001, 0, 10, 30, 100],
        labels=band_labels,
        include_lowest=True
    )

    discount_summary = (
        valid_discount.groupby("DiscountBand", observed=True)
        .agg(
            Observations=("sale_amount", "size"),
            AvgSales=("sale_amount", "mean"),
            StockoutRatePct=("HasStockout", "mean")
        )
        .reset_index()
    )
    discount_summary["StockoutRatePct"] *= 100

    high_discount_rate = discount_summary.loc[
        discount_summary["DiscountBand"] == "High (>30%)",
        "StockoutRatePct"
    ]

    no_discount_rate = discount_summary.loc[
        discount_summary["DiscountBand"] == "No discount",
        "StockoutRatePct"
    ]

    k1, k2, k3 = st.columns(3)
    k1.metric("Records analyzed", f"{len(filtered):,}")
    k2.metric("Invalid discount records excluded", f"{invalid_discount_count:,}")

    if not high_discount_rate.empty and not no_discount_rate.empty:
        difference = high_discount_rate.iloc[0] - no_discount_rate.iloc[0]
        k3.metric("High vs. no-discount stockout difference", f"{difference:+.2f} pp")
    else:
        k3.metric("High vs. no-discount stockout difference", "N/A")

    left, right = st.columns(2)

    with left:
        st.subheader("Average sales by discount group")
        fig_discount_sales = px.bar(
            discount_summary,
            x="DiscountBand",
            y="AvgSales",
            hover_data={"Observations": True},
            labels={
                "DiscountBand": "Discount group",
                "AvgSales": "Average observed sales"
            }
        )
        st.plotly_chart(fig_discount_sales, use_container_width=True)

    with right:
        st.subheader("Stockout rate by discount group")
        fig_discount_stockout = px.bar(
            discount_summary,
            x="DiscountBand",
            y="StockoutRatePct",
            hover_data={"Observations": True},
            labels={
                "DiscountBand": "Discount group",
                "StockoutRatePct": "Records with stockout (%)"
            }
        )
        st.plotly_chart(fig_discount_stockout, use_container_width=True)

    st.dataframe(
        discount_summary.round(3),
        use_container_width=True,
        hide_index=True
    )

    # So sánh doanh số trong và ngoài thời gian có activity, theo thành phố.
    activity_data = filtered.copy()
    activity_data["ActivityGroup"] = activity_data["activity_flag"].map(
        {0: "Normal", 1: "Activity"}
    )

    activity_by_city = (
        activity_data.groupby(["city_id", "ActivityGroup"])
        .agg(
            AvgSales=("sale_amount", "mean"),
            Observations=("sale_amount", "size")
        )
        .reset_index()
    )

    city_sales = activity_by_city.pivot(
        index="city_id",
        columns="ActivityGroup",
        values="AvgSales"
    ).reindex(columns=["Normal", "Activity"])

    city_sales["ActivityChangePct"] = (
        (city_sales["Activity"] / city_sales["Normal"] - 1) * 100
    ).where(city_sales["Normal"] != 0)

    cities_higher = int((city_sales["ActivityChangePct"] > 0).sum())
    cities_compared = int(city_sales["ActivityChangePct"].notna().sum())

    st.subheader("Activity and average sales by city")
    st.metric(
        "Cities with higher average sales during activity",
        f"{cities_higher} of {cities_compared}"
    )

    activity_chart_data = city_sales.reset_index().melt(
        id_vars="city_id",
        value_vars=["Normal", "Activity"],
        var_name="Period",
        value_name="AverageSales"
    )

    fig_activity = px.bar(
        activity_chart_data,
        x="city_id",
        y="AverageSales",
        color="Period",
        barmode="group",
        hover_data={"AverageSales": ":.3f"},
        labels={
            "city_id": "City ID",
            "AverageSales": "Average observed sales"
        }
    )
    st.plotly_chart(fig_activity, use_container_width=True)

    st.dataframe(
        city_sales.reset_index().round(2),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Discount bands are analyst-defined: 0%, >0–10%, >10–30%, and >30%. "
        "Invalid discounts outside 0–100% are excluded from discount comparisons. "
        "Activity results are compared by city because the relationship may differ "
        "across locations. These are observational associations; correlation does "
        "not prove that discounts or activities caused sales or stockout changes."
    )