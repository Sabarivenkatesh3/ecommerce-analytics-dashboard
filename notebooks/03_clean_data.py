import pandas as pd
import sqlite3

conn = sqlite3.connect("ecommerce.db")

print("=" * 50)
print("        DATA CLEANING REPORT")
print("=" * 50)

# ── Load orders ────────────────────────────────────────────────────
orders = pd.read_sql("SELECT * FROM orders", conn)

# ── 1. Check missing values ────────────────────────────────────────
print("\n🔍 MISSING VALUES IN ORDERS TABLE")
print("-" * 35)
missing = orders.isnull().sum()
missing_pct = (orders.isnull().sum() / len(orders) * 100).round(2)
missing_report = pd.DataFrame({
    "missing_count" : missing,
    "missing_pct"   : missing_pct
})
print(missing_report[missing_report["missing_count"] > 0].to_string())

# ── 2. Fix datetime columns ────────────────────────────────────────
print("\n🕐 CONVERTING DATE COLUMNS")
print("-" * 35)
date_cols = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]
for col in date_cols:
    orders[col] = pd.to_datetime(orders[col], errors="coerce")
    print(f"  ✅ {col} converted")

# ── 3. Add useful columns ──────────────────────────────────────────
print("\n➕ ADDING CALCULATED COLUMNS")
print("-" * 35)

# Month-Year for trend analysis
orders["order_month"] = orders["order_purchase_timestamp"].dt.to_period("M").astype(str)

# Day of week (0=Monday, 6=Sunday)
orders["order_day_of_week"] = orders["order_purchase_timestamp"].dt.day_name()

# Hour of day
orders["order_hour"] = orders["order_purchase_timestamp"].dt.hour

# Delivery time in days (actual)
orders["actual_delivery_days"] = (
    orders["order_delivered_customer_date"] -
    orders["order_purchase_timestamp"]
).dt.days

# Was delivery on time? (1=yes, 0=no)
orders["is_on_time"] = (
    orders["order_delivered_customer_date"] <=
    orders["order_estimated_delivery_date"]
).astype(int)

print("  ✅ order_month added")
print("  ✅ order_day_of_week added")
print("  ✅ order_hour added")
print("  ✅ actual_delivery_days added")
print("  ✅ is_on_time added")

# ── 4. Keep only delivered orders for analysis ─────────────────────
orders_clean = orders[orders["order_status"] == "delivered"].copy()
print(f"\n  ✅ Filtered to delivered orders only: {len(orders_clean):,} rows")

# ── 5. Save cleaned data back to database ─────────────────────────
orders_clean.to_sql("orders_clean", conn, if_exists="replace", index=False)
print("\n  ✅ orders_clean table saved to database")

# ── 6. Quick summary of cleaned data ──────────────────────────────
print("\n📊 CLEANED DATA SUMMARY")
print("-" * 35)
print(f"  Total delivered orders  : {len(orders_clean):,}")
print(f"  Date range              : {orders_clean['order_purchase_timestamp'].min().date()} → {orders_clean['order_purchase_timestamp'].max().date()}")
print(f"  Avg delivery days       : {orders_clean['actual_delivery_days'].mean():.1f} days")
print(f"  On-time delivery rate   : {orders_clean['is_on_time'].mean()*100:.1f}%")
print(f"  Busiest day             : {orders_clean['order_day_of_week'].mode()[0]}")
print(f"  Busiest hour            : {orders_clean['order_hour'].mode()[0]}:00")

conn.close()
print("\n" + "=" * 50)
print("  ✅ Data cleaning complete!")
print("=" * 50)