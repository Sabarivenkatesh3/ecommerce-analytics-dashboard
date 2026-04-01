import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import sqlite3
import os

# ── Setup ──────────────────────────────────────────────────────────
conn = sqlite3.connect("ecommerce.db")
os.makedirs("outputs", exist_ok=True)

plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"]   = "#f8f9fa"
plt.rcParams["axes.grid"]        = True
plt.rcParams["grid.alpha"]       = 0.4
plt.rcParams["font.family"]      = "sans-serif"

print("=" * 50)
print("     GENERATING ANALYSIS CHARTS")
print("=" * 50)

# ── Chart 1: Monthly Revenue Trend ────────────────────────────────
monthly = pd.read_sql("""
    SELECT
        o.order_month,
        COUNT(DISTINCT o.order_id)     AS total_orders,
        ROUND(SUM(p.payment_value), 2) AS revenue
    FROM orders_clean o
    JOIN payments p ON o.order_id = p.order_id
    GROUP BY o.order_month
    ORDER BY o.order_month
""", conn)

fig, ax1 = plt.subplots(figsize=(14, 5))
ax2 = ax1.twinx()

ax1.fill_between(monthly["order_month"], monthly["revenue"],
                 alpha=0.3, color="#2196F3")
ax1.plot(monthly["order_month"], monthly["revenue"],
         color="#2196F3", linewidth=2.5, marker="o", markersize=4, label="Revenue (R$)")
ax2.bar(monthly["order_month"], monthly["total_orders"],
        alpha=0.25, color="#FF9800", label="Orders")

ax1.set_title("Monthly Revenue & Order Volume Trend", fontsize=14, fontweight="bold", pad=15)
ax1.set_xlabel("Month", fontsize=11)
ax1.set_ylabel("Revenue (R$)", color="#2196F3", fontsize=11)
ax2.set_ylabel("Total Orders", color="#FF9800", fontsize=11)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R${x:,.0f}"))
plt.xticks(rotation=45, ha="right", fontsize=8)
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")
plt.tight_layout()
plt.savefig("outputs/01_monthly_revenue_trend.png", dpi=150, bbox_inches="tight")
plt.close()
print("\n  ✅ Chart 1 saved: Monthly Revenue Trend")

# ── Chart 2: Top 10 Categories by Revenue ─────────────────────────
categories = pd.read_sql("""
    SELECT
        COALESCE(c.product_category_name_english, 'unknown') AS category,
        ROUND(SUM(oi.price), 2) AS revenue
    FROM order_items oi
    JOIN products pr  ON oi.product_id = pr.product_id
    LEFT JOIN category c ON pr.product_category_name = c.product_category_name
    GROUP BY category
    ORDER BY revenue DESC
    LIMIT 10
""", conn)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(categories["category"][::-1], categories["revenue"][::-1],
               color=plt.cm.Blues(range(80, 255, 17)), edgecolor="white")
for bar, val in zip(bars, categories["revenue"][::-1]):
    ax.text(bar.get_width() + 5000, bar.get_y() + bar.get_height()/2,
            f"R${val:,.0f}", va="center", fontsize=9, color="#333")
ax.set_title("Top 10 Product Categories by Revenue", fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Total Revenue (R$)", fontsize=11)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R${x:,.0f}"))
plt.tight_layout()
plt.savefig("outputs/02_top_categories_revenue.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✅ Chart 2 saved: Top 10 Categories")

# ── Chart 3: Order Volume by Day of Week ──────────────────────────
dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
dow = pd.read_sql("""
    SELECT order_day_of_week, COUNT(*) AS total_orders
    FROM orders_clean
    GROUP BY order_day_of_week
""", conn)
dow["order_day_of_week"] = pd.Categorical(dow["order_day_of_week"],
                                           categories=dow_order, ordered=True)
dow = dow.sort_values("order_day_of_week")

fig, ax = plt.subplots(figsize=(10, 5))
colors = ["#FF5722" if d == "Monday" else "#2196F3" for d in dow["order_day_of_week"]]
bars = ax.bar(dow["order_day_of_week"], dow["total_orders"], color=colors, edgecolor="white")
for bar, val in zip(bars, dow["total_orders"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
            f"{val:,}", ha="center", fontsize=9)
ax.set_title("Order Volume by Day of Week\n(Monday is peak — highlighted in orange)",
             fontsize=13, fontweight="bold", pad=15)
ax.set_ylabel("Total Orders", fontsize=11)
plt.tight_layout()
plt.savefig("outputs/03_orders_by_day.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✅ Chart 3 saved: Orders by Day of Week")

# ── Chart 4: Review Score Distribution ────────────────────────────
reviews = pd.read_sql("""
    SELECT review_score, COUNT(*) AS count
    FROM reviews
    GROUP BY review_score
    ORDER BY review_score
""", conn)

colors_rv = ["#F44336","#FF9800","#FFC107","#8BC34A","#4CAF50"]
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(reviews["review_score"].astype(str), reviews["count"],
              color=colors_rv, edgecolor="white", width=0.6)
for bar, val in zip(bars, reviews["count"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
            f"{val:,}", ha="center", fontsize=10, fontweight="bold")
ax.set_title("Customer Review Score Distribution", fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Review Score (1=Worst, 5=Best)", fontsize=11)
ax.set_ylabel("Number of Reviews", fontsize=11)
plt.tight_layout()
plt.savefig("outputs/04_review_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✅ Chart 4 saved: Review Score Distribution")

# ── Chart 5: Delivery Performance ─────────────────────────────────
delivery = pd.read_sql("""
    SELECT
        CASE WHEN is_on_time = 1 THEN 'On Time' ELSE 'Late' END AS status,
        COUNT(*) AS count
    FROM orders_clean
    WHERE actual_delivery_days IS NOT NULL
    GROUP BY is_on_time
""", conn)

fig, ax = plt.subplots(figsize=(7, 7))
colors_d = ["#4CAF50", "#F44336"]
wedges, texts, autotexts = ax.pie(
    delivery["count"],
    labels=delivery["status"],
    autopct="%1.1f%%",
    colors=colors_d,
    startangle=90,
    wedgeprops={"edgecolor": "white", "linewidth": 2}
)
for text in autotexts:
    text.set_fontsize(13)
    text.set_fontweight("bold")
ax.set_title("Delivery Performance\nOn-Time vs Late Orders",
             fontsize=14, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig("outputs/05_delivery_performance.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✅ Chart 5 saved: Delivery Performance")

# ── Chart 6: Orders by Hour of Day ────────────────────────────────
hourly = pd.read_sql("""
    SELECT order_hour, COUNT(*) AS total_orders
    FROM orders_clean
    GROUP BY order_hour
    ORDER BY order_hour
""", conn)

fig, ax = plt.subplots(figsize=(12, 5))
colors_h = ["#FF5722" if h == 16 else "#2196F3" for h in hourly["order_hour"]]
ax.bar(hourly["order_hour"], hourly["total_orders"], color=colors_h, edgecolor="white")
ax.set_title("Order Volume by Hour of Day\n(4 PM is peak hour — highlighted in orange)",
             fontsize=13, fontweight="bold", pad=15)
ax.set_xlabel("Hour of Day (24hr)", fontsize=11)
ax.set_ylabel("Total Orders", fontsize=11)
ax.set_xticks(range(0, 24))
plt.tight_layout()
plt.savefig("outputs/06_orders_by_hour.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✅ Chart 6 saved: Orders by Hour of Day")

conn.close()
print("\n" + "=" * 50)
print("  ✅ All 6 charts saved to outputs/ folder")
print("  Open the outputs folder to see your charts!")
print("=" * 50)