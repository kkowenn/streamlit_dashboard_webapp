import streamlit as st
import pandas as pd
import altair as alt

# Load datasets
products_df = pd.read_csv("dataset/products.csv")
stores_df = pd.read_csv("dataset/stores.csv")
transactions_df = pd.read_csv("dataset/transactions.csv")

# Merge datasets
merged_df = transactions_df.merge(products_df, on="PROD_CODE").merge(stores_df, on="STORE_CODE")

# Convert SHOP_DATE to datetime
merged_df['SHOP_DATE'] = pd.to_datetime(merged_df['SHOP_DATE'], format='%Y%m%d')

# Calculate KPIs
total_spend = merged_df['SPEND'].sum()
total_basket = merged_df['BASKET_ID'].nunique()
avg_basket_size = merged_df.groupby('BASKET_ID')['SPEND'].sum().mean()

# Calculate date range for date filter
min_date = merged_df['SHOP_DATE'].min()
max_date = merged_df['SHOP_DATE'].max()

# Sidebar for date filtering
st.sidebar.header("Date Filter")
start_date = st.sidebar.date_input("Start Date", min_date)
end_date = st.sidebar.date_input("End Date", max_date)

# Filter data based on date range
filtered_df = merged_df[(merged_df['SHOP_DATE'] >= pd.to_datetime(start_date)) &
                        (merged_df['SHOP_DATE'] <= pd.to_datetime(end_date))]

# Calculate filtered KPIs
filtered_total_spend = filtered_df['SPEND'].sum()
filtered_total_basket = filtered_df['BASKET_ID'].nunique()
filtered_avg_basket_size = filtered_df.groupby('BASKET_ID')['SPEND'].sum().mean()

# KPIs
st.write("## Key Performance Indicators")
col1, col2, col3 = st.columns(3)
col1.metric("Total Spend", f"${filtered_total_spend:,.2f}")
col2.metric("Total Basket ", filtered_total_basket)
col3.metric("Avg Basket Size", f"${filtered_avg_basket_size:.2f}")

# Total Spend by Date
st.write("## Total Spend by Date")
total_spend_by_date = filtered_df.groupby('SHOP_DATE')['SPEND'].sum().reset_index()
st.line_chart(total_spend_by_date.rename(columns={'SHOP_DATE': 'index'}).set_index('index'))

# % Spend Difference
st.write("## % Spend Difference")
percent_spend_diff = filtered_df.groupby('PROD_CODE')['SPEND'].sum().pct_change().reset_index()
st.write(percent_spend_diff)

# Period-over-Period Spend
st.write("## Period-over-Period Spend")
pop_spend_chart = alt.Chart(filtered_df).mark_point().encode(
    x='SPEND',
    y='STORE_CODE',
    color='STORE_REGION'
).properties(width='container', height=400)
st.altair_chart(pop_spend_chart, use_container_width=True)

# Cumulative Spend by Product Code
st.write("## Cumulative Spend by Product Code")
cumulative_spend_by_product = filtered_df.groupby('PROD_CODE')['SPEND'].sum().reset_index()
cumulative_spend_chart = alt.Chart(cumulative_spend_by_product).mark_bar().encode(
    x='PROD_CODE',
    y='SPEND'
).properties(width='container', height=400)
st.altair_chart(cumulative_spend_chart, use_container_width=True)

# Diff 7d Spend by Store Region
st.write("## Diff 7d Spend by Store Region")
diff_spend_by_region = filtered_df.groupby('STORE_REGION')['SPEND'].sum().reset_index()
diff_spend_chart = alt.Chart(diff_spend_by_region).mark_bar().encode(
    x='STORE_REGION',
    y='SPEND',
    color=alt.condition(
        alt.datum.SPEND > 0,
        alt.value("green"),  # The positive color
        alt.value("red")     # The negative color
    )
).properties(width='container', height=400)
st.altair_chart(diff_spend_chart, use_container_width=True)

# Data Table
st.write("## Data Table")
st.dataframe(filtered_df)
