import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create data directory if not exists
os.makedirs("data", exist_ok=True)

# Set seed for reproducibility
np.random.seed(42)

# Parameters
num_transactions = 12000
num_customers = 800
countries = ['United Kingdom'] * 850 + ['Germany'] * 50 + ['France'] * 40 + ['Spain'] * 35 + ['Netherlands'] * 25

# Generate Customers database
customer_pool = [f"C{10000 + i}" for i in range(num_customers)]
customer_countries = {cust: np.random.choice(countries) for cust in customer_pool}

# Products data
products = [
    {"code": "22423", "desc": "REGENCY CAKESTAND 3 TIER", "price": 12.75},
    {"code": "85123A", "desc": "WHITE HANGING HEART T-LIGHT HOLDER", "price": 2.55},
    {"code": "71053", "desc": "WHITE METAL LANTERN", "price": 3.39},
    {"code": "84406B", "desc": "CREAM CUPID HEARTS COAT HANGER", "price": 2.75},
    {"code": "84029G", "desc": "KNITTED UNION FLAG HOT WATER BOTTLE", "price": 4.25},
    {"code": "37444A", "desc": "YELLOW BREAKFAST CUP AND SAUCER", "price": 2.95},
    {"code": "22752", "desc": "SET 7 BABUSHKA NESTING BOXES", "price": 8.50},
    {"code": "84879", "desc": "ASSORTED COLOUR BIRD ORNAMENT", "price": 1.69},
    {"code": "22386", "desc": "JUMBO BAG PINK POLKADOT", "price": 1.95},
    {"code": "20725", "desc": "LUNCH BAG RED RETROSPOT", "price": 1.65},
    {"code": "23203", "desc": "JUMBO BAG VINTAGE DOILY", "price": 2.05},
    {"code": "22662", "desc": "LUNCH BAG DOLLY GIRL DESIGN", "price": 1.65},
    {"code": "21731", "desc": "RED TOADSTOOL LED NIGHT LIGHT", "price": 1.25},
    {"code": "22961", "desc": "JAM MAKING SET PRINTED", "price": 1.45},
    {"code": "22382", "desc": "LUNCH BAG SPACEBOY DESIGN", "price": 1.65},
    {"code": "20727", "desc": "LUNCH BAG BLACK SKULL", "price": 1.65},
    {"code": "20728", "desc": "LUNCH BAG CARS BLUE", "price": 1.65},
    {"code": "22383", "desc": "LUNCH BAG SUKI DESIGN", "price": 1.65},
    {"code": "20726", "desc": "LUNCH BAG WOODLAND", "price": 1.65},
    {"code": "22960", "desc": "JAM MAKING SET WITH JARS", "price": 4.25}
]

# Generate transactions
invoice_numbers = [f"{536365 + i}" for i in range(3000)] # Invoice pools
data = []

# Date range: 2025-01-01 to 2026-06-01 (17 months)
start_date = datetime(2025, 1, 1)
end_date = datetime(2026, 6, 1)
delta_days = (end_date - start_date).days

# To simulate realistic cohorts, some customers will only buy in earlier months, some throughout
customer_join_date = {}
for cust in customer_pool:
    # Randomly assign a "signup" or "first purchase" date to each customer
    # Heavily weight towards earlier months to see retention trends
    join_day = int(np.random.beta(1.5, 3) * delta_days)
    customer_join_date[cust] = start_date + timedelta(days=join_day)

for _ in range(num_transactions):
    cust = np.random.choice(customer_pool)
    join_date = customer_join_date[cust]
    
    # Invoice date must be on or after customer's join date
    allowed_days = (end_date - join_date).days
    if allowed_days <= 0:
        tx_date = join_date
    else:
        tx_date = join_date + timedelta(days=int(np.random.exponential(scale=60) % allowed_days))
        
    # Introduce small probability of cancellation (Invoice starts with 'C')
    is_cancelled = np.random.rand() < 0.03
    
    # Group into purchase invoices
    invoice_idx = np.random.randint(0, len(invoice_numbers))
    inv_no = invoice_numbers[invoice_idx]
    if is_cancelled:
        inv_no = "C" + inv_no
        
    prod = np.random.choice(products)
    quantity = int(np.random.negative_binomial(5, 0.3) + 1)
    if is_cancelled:
        quantity = -quantity # negative for returns
        
    # Add slight random price fluctuation or discount
    unit_price = round(prod["price"] * np.random.choice([0.9, 1.0, 1.1], p=[0.1, 0.8, 0.1]), 2)
    
    # Introduce some missing customer IDs to teach data cleaning
    cust_id = cust
    if np.random.rand() < 0.05:
        cust_id = np.nan
        
    data.append({
        "InvoiceNo": inv_no,
        "StockCode": prod["code"],
        "Description": prod["desc"],
        "Quantity": quantity,
        "InvoiceDate": tx_date.strftime("%Y-%m-%d %H:%M"),
        "UnitPrice": unit_price,
        "CustomerID": cust_id,
        "Country": customer_countries[cust]
    })

df = pd.DataFrame(data)

# Sort transactions by date
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df = df.sort_values(by='InvoiceDate').reset_index(drop=True)
df['InvoiceDate'] = df['InvoiceDate'].dt.strftime("%Y-%m-%d %H:%M")

output_path = os.path.join("data", "raw_transactions.csv")
df.to_csv(output_path, index=False)
print(f"Generated {len(df)} transactions in {output_path}")
print(f"Unique customers: {df['CustomerID'].dropna().nunique()}")
