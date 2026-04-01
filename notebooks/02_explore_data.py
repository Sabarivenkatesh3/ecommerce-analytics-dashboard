import pandas as pd
import sqlite3

# ── Connect to database ────────────────────────────────────────────
conn = sqlite3.connect("ecommerce.db")

print("=" * 50)
print("   EXPLORATORY DATA ANALYSIS REPORT")
print("=" * 50)

# ── 1. Order Status Breakdown ──────────────────────────────────────
print("\n📦 ORDER STATUS BREAKDOWN")
print("-" * 35)
status = pd.read_sql("""
    SELECT order_status,
           COUNT(*) as total_orders,
           ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) as percentage
    FROM orders
    GROUP BY order_status
    ORDER BY total_orders DESC
""", conn)
print(status.to_string(index=False))

# ── 2. Revenue Overview ────────────────────────────────────────────
print("\n💰 REVENUE OVERVIEW")
print("-" * 35)
revenue = pd.read_sql("""
    SELECT
        ROUND(SUM(payment_value), 2)   AS total_revenue,
        ROUND(AVG(payment_value), 2)   AS avg_order_value,
        ROUND(MIN(payment_value), 2)   AS min_order_value,
        ROUND(MAX(payment_value), 2)   AS max_order_value,
        COUNT(DISTINCT order_id)       AS total_orders
    FROM payments
""", conn)
print(revenue.to_string(index=False))

# ── 3. Monthly Revenue Trend ───────────────────────────────────────
print("\n📅 MONTHLY REVENUE TREND (Top 12 months)")
print("-" * 35)
monthly = pd.read_sql("""
    SELECT
        SUBSTR(o.order_purchase_timestamp, 1, 7) AS month,
        COUNT(DISTINCT o.order_id)               AS total_orders,
        ROUND(SUM(p.payment_value), 2)           AS revenue
    FROM orders o
    JOIN payments p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY month
    ORDER BY month DESC
    LIMIT 12
""", conn)
print(monthly.to_string(index=False))

# ── 4. Top 10 Product Categories ──────────────────────────────────
print("\n🏷️  TOP 10 PRODUCT CATEGORIES BY REVENUE")
print("-" * 35)
categories = pd.read_sql("""
    SELECT
        COALESCE(c.product_category_name_english, 'unknown') AS category,
        COUNT(DISTINCT oi.order_id)                          AS total_orders,
        ROUND(SUM(oi.price), 2)                              AS total_revenue
    FROM order_items oi
    JOIN products pr ON oi.product_id = pr.product_id
    LEFT JOIN category c ON pr.product_category_name = c.product_category_name
    GROUP BY category
    ORDER BY total_revenue DESC
    LIMIT 10
""", conn)
print(categories.to_string(index=False))

# ── 5. Delivery Performance ────────────────────────────────────────
print("\n🚚 DELIVERY PERFORMANCE")
print("-" * 35)
delivery = pd.read_sql("""
    SELECT
        COUNT(*) AS total_delivered,
        SUM(CASE
            WHEN order_delivered_customer_date <= order_estimated_delivery_date
            THEN 1 ELSE 0 END) AS on_time,
        SUM(CASE
            WHEN order_delivered_customer_date > order_estimated_delivery_date
            THEN 1 ELSE 0 END) AS late,
        ROUND(SUM(CASE
            WHEN order_delivered_customer_date <= order_estimated_delivery_date
            THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS on_time_pct
    FROM orders
    WHERE order_status = 'delivered'
      AND order_delivered_customer_date IS NOT NULL
""", conn)
print(delivery.to_string(index=False))

# ── 6. Customer Review Scores ──────────────────────────────────────
print("\n⭐ CUSTOMER REVIEW SCORE DISTRIBUTION")
print("-" * 35)
reviews = pd.read_sql("""
    SELECT
        review_score,
        COUNT(*)                                              AS total_reviews,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reviews), 2) AS percentage
    FROM reviews
    GROUP BY review_score
    ORDER BY review_score DESC
""", conn)
print(reviews.to_string(index=False))

conn.close()
print("\n" + "=" * 50)
print("   ✅ Exploration complete!")
print("=" * 50)