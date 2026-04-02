import streamlit as st
import math
import pandas as pd

st.title("📦 Supply Chain AI Tool")

# Premium header
st.markdown("""
### 📊 AI-Powered Inventory Optimization

This tool helps optimize inventory decisions using:
- Service level based safety stock
- Reorder point calculation
- AI-driven recommendations
- Automated purchase order suggestions

👉 Upload your data and simulate decisions in real-time.
""")

# Sidebar
st.sidebar.header("⚙️ Controls")

service_level = st.sidebar.selectbox(
    "Service Level",
    ["90%", "95%", "99%"],
    index=1
)

# Z values
if service_level == "90%":
    Z = 1.28
elif service_level == "95%":
    Z = 1.65
else:
    Z = 2.33

# AI insight
def get_ai_insight(status):
    if status == "🔴 Stockout Risk":
        return "Stock is below required level. Recommend immediate replenishment and review safety stock."
    elif status == "🟡 Excess Inventory":
        return "Inventory is higher than needed. Consider reducing orders or running promotions."
    else:
        return "Inventory levels are healthy. Maintain current planning strategy."

# Upload
uploaded_file = st.file_uploader("Upload inventory CSV", type=["csv"])

if uploaded_file is not None:
    input_df = pd.read_csv(uploaded_file)
else:
    input_df = pd.read_csv("inventory_data.csv")

# Normalize columns
input_df.columns = input_df.columns.str.strip().str.lower().str.replace(" ", "_")

results = []

# Loop
for _, row in input_df.iterrows():
    sku = row["sku"]
    avg_demand = row["demand"]
    lead_time = row["lead_time"]

    stock = st.slider(
        f"Stock for SKU {sku}",
        min_value=0,
        max_value=2000,
        value=int(row["current_stock"])
    )

    std_dev = avg_demand * 0.2

    safety_stock = Z * std_dev * math.sqrt(lead_time)
    reorder_point = avg_demand * lead_time + safety_stock

    if stock < reorder_point:
        status = "🔴 Stockout Risk"
        status_color = "red"
    elif stock > reorder_point * 1.5:
        status = "🟡 Excess Inventory"
        status_color = "orange"
    else:
        status = "🟢 Healthy"
        status_color = "green"

    insight = get_ai_insight(status)

    results.append({
        "SKU": sku,
        "Avg Demand": round(avg_demand, 2),
        "Safety Stock": round(safety_stock, 2),
        "Reorder Point": round(reorder_point, 2),
        "Stock": stock,
        "Status": status,
        "Status Color": status_color,
        "AI Insight": insight
    })

df = pd.DataFrame(results)

# Filter
selected_sku = st.selectbox("Select SKU", ["All"] + list(df["SKU"]))

if selected_sku != "All":
    filtered_df = df[df["SKU"] == selected_sku]
else:
    filtered_df = df

# KPIs
total_skus = len(filtered_df)
stockout_count = len(filtered_df[filtered_df["Status"] == "🔴 Stockout Risk"])
excess_count = len(filtered_df[filtered_df["Status"] == "🟡 Excess Inventory"])

col1, col2, col3 = st.columns(3)

col1.metric("Total SKUs", total_skus)
col2.metric("Stockout Risk", stockout_count)
col3.metric("Excess Inventory", excess_count)

# Key Insight
st.subheader("📌 Key Insight")

if stockout_count > 0:
    st.warning(f"{stockout_count} SKUs are at risk of stockout. Immediate action recommended.")
elif excess_count > 0:
    st.info(f"{excess_count} SKUs have excess inventory. Opportunity to optimize working capital.")
else:
    st.success("Inventory is well balanced across all SKUs.")

# Styled table
def highlight_status(row):
    color = row["Status Color"]
    return ["background-color: %s" % color if col == "Status" else "" for col in row.index]

styled_df = filtered_df.style.apply(highlight_status, axis=1)

st.subheader("Inventory Insights")
st.dataframe(styled_df, use_container_width=True)

# AI recommendations
st.subheader("Detailed AI Recommendations")

for _, row in filtered_df.iterrows():
    st.markdown(f"### SKU {row['SKU']}")
    st.write(f"**Status:** {row['Status']}")
    st.info(row["AI Insight"])

# Charts
st.subheader("📊 Demand Overview")
st.bar_chart(filtered_df.set_index("SKU")["Avg Demand"])

st.subheader("📦 Stock vs Reorder Point")
chart_df = filtered_df.set_index("SKU")[["Stock", "Reorder Point"]]
st.bar_chart(chart_df)

st.subheader("🚨 Risk Status Count")
status_count = filtered_df["Status"].value_counts()
st.bar_chart(status_count)

# PO Suggestions
st.subheader("🧾 Auto Purchase Order Suggestions")

po_results = []

for _, row in filtered_df.iterrows():
    suggested_order_qty = max(0, round(row["Reorder Point"] - row["Stock"], 0))

    if suggested_order_qty > 0:
        po_results.append({
            "SKU": row["SKU"],
            "Current Stock": row["Stock"],
            "Reorder Point": row["Reorder Point"],
            "Suggested Order Qty": suggested_order_qty,
            "Action": "Create PO"
        })

po_df = pd.DataFrame(po_results)

if len(po_df) > 0:
    st.dataframe(po_df, use_container_width=True)
else:
    st.write("No purchase orders needed right now.")

# Download
if len(po_df) > 0:
    csv = po_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Purchase Orders (CSV)",
        data=csv,
        file_name="purchase_orders.csv",
        mime="text/csv"
    )
