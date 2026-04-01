import pandas as pd
import sqlite3
import os

# ── Load all CSV files ─────────────────────────────────────────────
data_path = "data/"

orders      = pd.read_csv(data_path + "olist_orders_dataset.csv")
customers   = pd.read_csv(data_path + "olist_customers_dataset.csv")
order_items = pd.read_csv(data_path + "olist_order_items_dataset.csv")
payments    = pd.read_csv(data_path + "olist_order_payments_dataset.csv")
products    = pd.read_csv(data_path + "olist_products_dataset.csv")
sellers     = pd.read_csv(data_path + "olist_sellers_dataset.csv")
reviews     = pd.read_csv(data_path + "olist_order_reviews_dataset.csv")
category    = pd.read_csv(data_path + "product_category_name_translation.csv")

print("=" * 45)
print("      DATA LOADING REPORT")
print("=" * 45)
print(f"  Orders        : {orders.shape[0]:,} rows, {orders.shape[1]} columns")
print(f"  Customers     : {customers.shape[0]:,} rows, {customers.shape[1]} columns")
print(f"  Order Items   : {order_items.shape[0]:,} rows, {order_items.shape[1]} columns")
print(f"  Payments      : {payments.shape[0]:,} rows, {payments.shape[1]} columns")
print(f"  Products      : {products.shape[0]:,} rows, {products.shape[1]} columns")
print(f"  Sellers       : {sellers.shape[0]:,} rows, {sellers.shape[1]} columns")
print(f"  Reviews       : {reviews.shape[0]:,} rows, {reviews.shape[1]} columns")
print(f"  Categories    : {category.shape[0]:,} rows, {category.shape[1]} columns")
print("=" * 45)

# ── Load into SQLite database ──────────────────────────────────────
conn = sqlite3.connect("ecommerce.db")

orders.to_sql("orders",           conn, if_exists="replace", index=False)
customers.to_sql("customers",     conn, if_exists="replace", index=False)
order_items.to_sql("order_items", conn, if_exists="replace", index=False)
payments.to_sql("payments",       conn, if_exists="replace", index=False)
products.to_sql("products",       conn, if_exists="replace", index=False)
sellers.to_sql("sellers",         conn, if_exists="replace", index=False)
reviews.to_sql("reviews",         conn, if_exists="replace", index=False)
category.to_sql("category",       conn, if_exists="replace", index=False)

conn.close()

print("\n  ✅ ecommerce.db created successfully")
print("  ✅ All 8 tables loaded into SQLite")
print("\n  Your project database is ready!")
print("=" * 45)