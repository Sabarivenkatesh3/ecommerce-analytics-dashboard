import pandas as pd
import sqlite3
import os

conn = sqlite3.connect("ecommerce.db")
os.makedirs("outputs", exist_ok=True)

print("=" * 50)
print("     EXPORTING DATA FOR POWER BI")
print("=" * 50)

# ── 1. Monthly Revenue Summary ─────────────────────────────────────
monthly_revenue = pd.read_sql("""
    SELECT
        o.order_month,
        COUNT(DISTINCT o.order_id)     AS total_orders,
        ROUND(SUM(p.payment_value), 2) AS revenue,
        ROUND(AVG(p.payment_value), 2) AS avg_order_value
    FROM orders_clean o
    JOIN payments p ON o.order_id = p.order_id
    GROUP BY o.order_month
    ORDER BY o.order_month
""", conn)
monthly_revenue.to_excel("outputs/01_monthly_revenue.xlsx", index=False)
print(f"\n  ✅ Monthly Revenue     : {len(monthly_revenue)} rows")

# ── 2. Category Performance ────────────────────────────────────────
category_perf = pd.read_sql("""
    SELECT
        COALESCE(c.product_category_name_english, 'unknown') AS category,
        COUNT(DISTINCT oi.order_id)                          AS total_orders,
        ROUND(SUM(oi.price), 2)                              AS total_revenue,
        ROUND(AVG(oi.price), 2)                              AS avg_price,
        ROUND(AVG(r.review_score), 2)                        AS avg_review_score
    FROM order_items oi
    JOIN products pr     ON oi.product_id      = pr.product_id
    LEFT JOIN category c ON pr.product_category_name = c.product_category_name
    LEFT JOIN reviews r  ON oi.order_id        = r.order_id
    GROUP BY category
    ORDER BY total_revenue DESC
""", conn)
category_perf.to_excel("outputs/02_category_performance.xlsx", index=False)
print(f"  ✅ Category Performance: {len(category_perf)} rows")

# ── 3. Delivery Performance by Month ──────────────────────────────
delivery_perf = pd.read_sql("""
    SELECT
        order_month,
        COUNT(*)                                AS total_orders,
        SUM(is_on_time)                         AS on_time_orders,
        COUNT(*) - SUM(is_on_time)              AS late_orders,
        ROUND(AVG(is_on_time) * 100, 2)         AS on_time_pct,
        ROUND(AVG(actual_delivery_days), 1)     AS avg_delivery_days
    FROM orders_clean
    WHERE actual_delivery_days IS NOT NULL
    GROUP BY order_month
    ORDER BY order_month
""", conn)
delivery_perf.to_excel("outputs/03_delivery_performance.xlsx", index=False)
print(f"  ✅ Delivery Performance: {len(delivery_perf)} rows")

# ── 4. Customer Review Analysis ────────────────────────────────────
review_analysis = pd.read_sql("""
    SELECT
        o.order_month,
        ROUND(AVG(r.review_score), 2)           AS avg_review_score,
        COUNT(r.review_id)                       AS total_reviews,
        SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) AS five_star,
        SUM(CASE WHEN r.review_score = 1 THEN 1 ELSE 0 END) AS one_star
    FROM orders_clean o
    JOIN reviews r ON o.order_id = r.order_id
    GROUP BY o.order_month
    ORDER BY o.order_month
""", conn)
review_analysis.to_excel("outputs/04_review_analysis.xlsx", index=False)
print(f"  ✅ Review Analysis     : {len(review_analysis)} rows")

# ── 5. Seller Performance ──────────────────────────────────────────
seller_perf = pd.read_sql("""
    SELECT
        oi.seller_id,
        s.seller_city,
        s.seller_state,
        COUNT(DISTINCT oi.order_id)       AS total_orders,
        ROUND(SUM(oi.price), 2)           AS total_revenue,
        ROUND(AVG(r.review_score), 2)     AS avg_review_score
    FROM order_items oi
    JOIN sellers s  ON oi.seller_id  = s.seller_id
    LEFT JOIN reviews r ON oi.order_id = r.order_id
    GROUP BY oi.seller_id, s.seller_city, s.seller_state
    ORDER BY total_revenue DESC
    LIMIT 100
""", conn)
seller_perf.to_excel("outputs/05_seller_performance.xlsx", index=False)
print(f"  ✅ Seller Performance  : {len(seller_perf)} rows")

# ── 6. Full clean dataset for Power BI ────────────────────────────
full_data = pd.read_sql("""
    SELECT
        o.order_id,
        o.order_month,
        o.order_day_of_week,
        o.order_hour,
        o.actual_delivery_days,
        o.is_on_time,
        o.order_status,
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
    JOIN payments p      ON o.order_id  = p.order_id
    JOIN order_items oi  ON o.order_id  = oi.order_id
    JOIN products pr     ON oi.product_id = pr.product_id
    LEFT JOIN category c ON pr.product_category_name = c.product_category_name
    LEFT JOIN reviews r  ON o.order_id  = r.order_id
    JOIN sellers s       ON oi.seller_id = s.seller_id
    JOIN customers cu    ON o.customer_id = cu.customer_id
""", conn)
full_data.to_excel("outputs/06_full_dataset_powerbi.xlsx", index=False)
print(f"  ✅ Full Dataset        : {len(full_data):,} rows")

conn.close()
print("\n" + "=" * 50)
print("  ✅ All files exported to outputs/ folder")
print("  Ready to open in Power BI!")
print("=" * 50)