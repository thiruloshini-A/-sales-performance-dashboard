"""
Sales Performance Analysis
---------------------------
Analyzes 50,000+ retail sales records to identify top products,
regional trends, seasonal patterns, and underperforming categories.

Tech: Python (Pandas), SQL (via sqlite3), Matplotlib/Seaborn
"""
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110

# ----------------------------------------------------------------
# 1. Load data
# ----------------------------------------------------------------
df = pd.read_csv("data/sales_data.csv", parse_dates=["OrderDate"])
df["Month"] = df["OrderDate"].dt.to_period("M").astype(str)
print(f"Loaded {len(df):,} rows | {df['OrderDate'].min().date()} to {df['OrderDate'].max().date()}")

# ----------------------------------------------------------------
# 2. Load into SQLite to demonstrate SQL querying (joins/aggregations)
# ----------------------------------------------------------------
conn = sqlite3.connect(":memory:")
df.to_sql("sales", conn, index=False, if_exists="replace")

# Top 10 products by revenue
top_products_sql = """
    SELECT Product, Category, SUM(Revenue) AS TotalRevenue, SUM(Quantity) AS UnitsSold
    FROM sales
    GROUP BY Product, Category
    ORDER BY TotalRevenue DESC
    LIMIT 10;
"""
top_products = pd.read_sql(top_products_sql, conn)
print("\n--- Top 10 Products by Revenue ---")
print(top_products.to_string(index=False))

# Revenue by region
region_sql = """
    SELECT Region, SUM(Revenue) AS TotalRevenue, COUNT(*) AS Orders,
           ROUND(AVG(Revenue),2) AS AvgOrderValue
    FROM sales
    GROUP BY Region
    ORDER BY TotalRevenue DESC;
"""
region_summary = pd.read_sql(region_sql, conn)
print("\n--- Revenue by Region ---")
print(region_summary.to_string(index=False))

# Category performance (to flag underperformers)
category_sql = """
    SELECT Category, SUM(Revenue) AS TotalRevenue, SUM(Quantity) AS UnitsSold,
           ROUND(AVG(Revenue),2) AS AvgOrderValue
    FROM sales
    GROUP BY Category
    ORDER BY TotalRevenue ASC;
"""
category_summary = pd.read_sql(category_sql, conn)
print("\n--- Category Performance (lowest first) ---")
print(category_summary.to_string(index=False))

underperformers = category_summary.head(3)["Category"].tolist()
print(f"\n>>> Underperforming categories flagged: {underperformers}")

# Monthly revenue trend (seasonality)
monthly_sql = """
    SELECT Month, SUM(Revenue) AS TotalRevenue
    FROM sales
    GROUP BY Month
    ORDER BY Month;
"""
monthly_trend = pd.read_sql(monthly_sql, conn)

conn.close()

# ----------------------------------------------------------------
# 3. Visualizations
# ----------------------------------------------------------------

# Chart 1: Monthly revenue trend
plt.figure(figsize=(11, 5))
plt.plot(monthly_trend["Month"], monthly_trend["TotalRevenue"], marker="o", color="#2E86AB")
plt.xticks(rotation=45, ha="right")
plt.title("Monthly Revenue Trend (2023-2024)")
plt.ylabel("Revenue (₹)")
plt.tight_layout()
plt.savefig("charts/monthly_revenue_trend.png")
plt.close()

# Chart 2: Revenue by region
plt.figure(figsize=(7, 5))
sns.barplot(data=region_summary, x="Region", y="TotalRevenue", palette="viridis")
plt.title("Total Revenue by Region")
plt.ylabel("Revenue (₹)")
plt.tight_layout()
plt.savefig("charts/revenue_by_region.png")
plt.close()

# Chart 3: Category performance (highlight underperformers)
colors = ["#D64550" if c in underperformers else "#2E86AB" for c in category_summary["Category"]]
plt.figure(figsize=(9, 5))
plt.barh(category_summary["Category"], category_summary["TotalRevenue"], color=colors)
plt.title("Revenue by Category (Red = Underperforming)")
plt.xlabel("Revenue (₹)")
plt.tight_layout()
plt.savefig("charts/category_performance.png")
plt.close()

# Chart 4: Top 10 products
plt.figure(figsize=(9, 5))
sns.barplot(data=top_products, y="Product", x="TotalRevenue", palette="mako")
plt.title("Top 10 Products by Revenue")
plt.xlabel("Revenue (₹)")
plt.tight_layout()
plt.savefig("charts/top_10_products.png")
plt.close()

# Chart 5: Revenue distribution (per-order)
plt.figure(figsize=(8, 5))
sns.histplot(df["Revenue"], bins=50, color="#2E86AB", kde=True)
plt.title("Distribution of Order Revenue")
plt.xlabel("Revenue (₹)")
plt.ylabel("Number of Orders")
plt.tight_layout()
plt.savefig("charts/revenue_distribution.png")
plt.close()

# Chart 6: Unit price distribution by category
plt.figure(figsize=(9, 5))
sns.boxplot(data=df, x="Category", y="UnitPrice", palette="Set2")
plt.title("Unit Price Distribution by Category")
plt.xticks(rotation=30, ha="right")
plt.ylabel("Unit Price (₹)")
plt.tight_layout()
plt.savefig("charts/price_distribution_by_category.png")
plt.close()

print("\nCharts saved to /charts folder.")
print("Analysis complete.")
