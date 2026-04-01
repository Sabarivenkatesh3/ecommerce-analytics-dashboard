import pandas as pd
import sqlite3

conn = sqlite3.connect("ecommerce.db")

print("=" * 45)
print("   FIXING DAY ORDER + RE-EXPORTING DATA")
print("=" * 45)

# ── Load orders_clean ──────────────────────────────────────────────
orders_clean = pd.read_sql("SELECT * FROM orders_clean", conn)

# ── Add day_number column ──────────────────────────────────────────
day_order = {
    "Monday"    : 1,
    "Tuesday"   : 2,
    "Wednesday" : 3,
    "Thursday"  : 4,
    "Friday"    : 5,
    "Saturday"  : 6,
    "Sunday"    : 7
}
orders_clean["day_number"] = orders_clean["order_day_of_week"].map(day_order)

# Save back to database
orders_clean.to_sql("orders_clean", conn, if_exists="replace", index=False)
print("\n  ✅ day_number column added to orders_clean")

# ── Re-export full dataset WITH all columns including order_status ─
full_data = pd.read_sql("""
    SELECT
        o.order_id,
        o.order_status,
        o.order_month,
        o.order_day_of_week,
        o.day_number,
        o.order_hour,
        o.actual_delivery_days,
        o.is_on_time,
        p.payment_value,
        p.payment_type,
        COALESCE(c.product_category_name_english, 'unknown') AS category,
        oi.price,
        oi.freight_value,
        r.review_score,
        s.seller_city,
        s.seller_state,
        cu.customer_city,
        cu.customer_state
    FROM orders_clean o
    JOIN payments p      ON o.order_id    = p.order_id
    JOIN order_items oi  ON o.order_id    = oi.order_id
    JOIN products pr     ON oi.product_id = pr.product_id
    LEFT JOIN category c ON pr.product_category_name = c.product_category_name
    LEFT JOIN reviews r  ON o.order_id    = r.order_id
    JOIN sellers s       ON oi.seller_id  = s.seller_id
    JOIN customers cu    ON o.customer_id = cu.customer_id
""", conn)

full_data.to_excel("outputs/06_full_dataset_powerbi.xlsx", index=False)
conn.close()

print(f"  ✅ Full dataset exported: {len(full_data):,} rows")
print(f"  ✅ Columns included: {list(full_data.columns)}")
print("\n" + "=" * 45)
print("  ✅ All done! Now refresh Power BI.")
print("=" * 45)