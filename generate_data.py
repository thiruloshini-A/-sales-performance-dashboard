"""
Generates a synthetic retail sales dataset (~50,000 rows)
with realistic seasonal trends, regions, and product categories.
"""
import numpy as np
import pandas as pd

np.random.seed(42)

N = 50000

regions = ["North", "South", "East", "West", "Central"]
region_weights = [0.22, 0.28, 0.18, 0.20, 0.12]

categories = {
    "Electronics": ["Smartphone", "Laptop", "Headphones", "Smartwatch", "Tablet"],
    "Home & Kitchen": ["Mixer", "Cookware Set", "Vacuum Cleaner", "Air Fryer"],
    "Apparel": ["T-Shirt", "Jeans", "Jacket", "Sneakers"],
    "Beauty": ["Skincare Kit", "Perfume", "Hair Dryer"],
    "Groceries": ["Snack Pack", "Organic Coffee", "Cereal Box"],
    # Deliberately underperforming categories
    "Stationery": ["Notebook", "Pen Set", "Desk Organizer"],
    "Toys": ["Puzzle", "Action Figure", "Board Game"],
    "Furniture": ["Office Chair", "Bookshelf"],
}

cat_base_price = {
    "Electronics": (3000, 60000), "Home & Kitchen": (800, 12000),
    "Apparel": (300, 4000), "Beauty": (200, 3500),
    "Groceries": (50, 900), "Stationery": (30, 500),
    "Toys": (150, 2000), "Furniture": (2000, 25000),
}

# categories with deliberately weak sales (for the "3 underperforming categories" insight)
weak_categories = {"Stationery", "Toys", "Furniture"}

dates = pd.date_range("2023-01-01", "2024-12-31", freq="D")

rows = []
cat_list = list(categories.keys())
cat_probs = np.array([0.22, 0.16, 0.18, 0.14, 0.14, 0.06, 0.05, 0.05])
cat_probs = cat_probs / cat_probs.sum()

for i in range(N):
    date = np.random.choice(dates)
    date = pd.Timestamp(date)
    month = date.month

    # seasonal multiplier: boost in Nov-Dec (festive/holiday), dip in Feb
    seasonal_mult = 1.0
    if month in (11, 12):
        seasonal_mult = 1.6
    elif month == 2:
        seasonal_mult = 0.75
    elif month in (6, 7):
        seasonal_mult = 1.15

    category = np.random.choice(cat_list, p=cat_probs)
    product = np.random.choice(categories[category])
    region = np.random.choice(regions, p=region_weights)

    low, high = cat_base_price[category]
    unit_price = np.round(np.random.uniform(low, high), 2)

    qty = np.random.poisson(3) + 1
    if category in weak_categories:
        qty = max(1, int(qty * np.random.uniform(0.3, 0.5)))  # suppress qty
        seasonal_mult *= 0.6

    qty = max(1, int(qty * seasonal_mult))

    discount_pct = np.random.choice([0, 0, 0, 5, 10, 15, 20], p=[0.35,0.15,0.1,0.15,0.1,0.1,0.05])
    revenue = round(qty * unit_price * (1 - discount_pct / 100), 2)

    rows.append([
        date.strftime("%Y-%m-%d"), region, category, product,
        qty, unit_price, discount_pct, revenue
    ])

df = pd.DataFrame(rows, columns=[
    "OrderDate", "Region", "Category", "Product",
    "Quantity", "UnitPrice", "DiscountPct", "Revenue"
])

df.sort_values("OrderDate", inplace=True)
df.reset_index(drop=True, inplace=True)
df.insert(0, "OrderID", [f"ORD{100000+i}" for i in range(len(df))])

df.to_csv("data/sales_data.csv", index=False)
print(f"Generated {len(df):,} rows -> data/sales_data.csv")
print(df.head())
