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

# Sidebar controls
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

# AI insight function
def get_ai_insight(status):
    if status == "🔴 Stockout Risk":
        return "Stock is below required level. Recommend immediate replenishment and review safety stock."
    elif status == "🟡 Excess Inventory":
        return "Inventory is higher than needed. Consider reducing orders or running promotions."
    else:
        return "Inventory levels are healthy. Maintain current planning strategy."

# File upload
uploaded_file = st.file_uploader("Upload inventory CSV", type=["csv"])

if uploaded_file is not None:
    input_df = pd.read_csv(uploaded_file)
else:
    input_df = pd.read_csv("inventory_data.csv")

# Normalize columns
input_df.columns = input_df.columns.str.strip().str.lower().str.replace(" ", "_")

results = []

# Main loop
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

    # variability assumption
    std_dev = avg_demand * 0.2

    safety_stock = Z * std_dev * math.sqrt(lead_time)
    reorder_point = avg_demand * lead_time + safety_stock

    # status + color
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
selected_sku =
