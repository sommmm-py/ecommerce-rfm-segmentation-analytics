import os
import json
import pandas as pd
import numpy as np

def run_pipeline():
    print("=== APEX ANALYTICS: DATA PIPELINE STARTED ===")
    
    # 1. Load Raw Data
    raw_data_path = os.path.join("data", "raw_transactions.csv")
    if not os.path.exists(raw_data_path):
        raise FileNotFoundError(f"Raw data file not found at {raw_data_path}. Please run generate_data.py first.")
    
    df = pd.read_csv(raw_data_path)
    initial_rows = len(df)
    print(f"Loaded {initial_rows} raw transactions.")

    # 2. Data Cleaning
    # Drop rows without CustomerID
    df = df.dropna(subset=['CustomerID'])
    cleaned_rows = len(df)
    print(f"Dropped {initial_rows - cleaned_rows} rows with missing CustomerID.")

    # Convert InvoiceDate to datetime
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Exclude cancellations (InvoiceNo starting with 'C') for standard RFM
    # In retail analysis, returns are typically analyzed separately. 
    # For this dashboard, we will focus on positive transactions.
    df_sales = df[df['Quantity'] > 0].copy()
    print(f"Filtered out cancellations. Remaining sales records: {len(df_sales)}")

    # Calculate TotalSpend per line
    df_sales['TotalSpend'] = df_sales['Quantity'] * df_sales['UnitPrice']

    # 3. RFM Analysis
    # Reference date for Recency (1 day after the latest transaction date)
    reference_date = df_sales['InvoiceDate'].max() + pd.Timedelta(days=1)
    print(f"Reference date for Recency calculation: {reference_date.strftime('%Y-%m-%d')}")

    # Calculate Recency, Frequency, Monetary values per customer
    rfm = df_sales.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (reference_date - x.max()).days, # Recency
        'InvoiceNo': 'nunique',                                  # Frequency (Unique invoices)
        'TotalSpend': 'sum'                                      # Monetary
    }).rename(columns={
        'InvoiceDate': 'Recency',
        'InvoiceNo': 'Frequency',
        'TotalSpend': 'Monetary'
    }).reset_index()

    # Assign RFM Scores (1 to 5)
    # Recency: lower is better (more recent), so labels 5 to 1
    # Frequency & Monetary: higher is better, so labels 1 to 5
    
    # We use qcut (quantile-based discretization) to rank customers fairly.
    # Note: To avoid duplicate bin edge issues on frequency, we handle duplicates by ranking if needed,
    # or just using rank methods. Let's use rank-based qcut or duplicate-safe ranking.
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
    
    # For frequency, if we have many customers with low frequency, qcut can throw an edge error.
    # We can use ranking with pct=True or rank(method='first') to split them evenly.
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])

    # Convert to numeric scores
    rfm['R_Score'] = rfm['R_Score'].astype(int)
    rfm['F_Score'] = rfm['F_Score'].astype(int)
    rfm['M_Score'] = rfm['M_Score'].astype(int)

    # Segment customers based on R and F scores
    def segment_customer(row):
        r = row['R_Score']
        f = row['F_Score']
        
        if r >= 4 and f >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3:
            return 'Loyal Customers'
        elif r >= 3 and f <= 2:
            return 'Promising/New'
        elif r <= 2 and f >= 3:
            return 'At Risk'
        else:
            return 'Lost/Hibernating'

    rfm['Segment'] = rfm.apply(segment_customer, axis=1)

    # 4. Cohort Analysis (Monthly Retention)
    # Define cohort month and invoice month
    df_sales['InvoiceMonth'] = df_sales['InvoiceDate'].dt.to_period('M')
    df_sales['CohortMonth'] = df_sales.groupby('CustomerID')['InvoiceMonth'].transform('min')

    # Calculate index (difference in months)
    df_sales['CohortIndex'] = (df_sales['InvoiceMonth'].dt.year - df_sales['CohortMonth'].dt.year) * 12 + \
                               (df_sales['InvoiceMonth'].dt.month - df_sales['CohortMonth'].dt.month) + 1

    # Group and count unique customers per cohort
    cohort_group = df_sales.groupby(['CohortMonth', 'CohortIndex'])['CustomerID'].nunique().reset_index()
    
    # Pivot to cohort matrix
    cohort_matrix = cohort_group.pivot(index='CohortMonth', columns='CohortIndex', values='CustomerID')
    
    # Compute retention percentage
    cohort_sizes = cohort_matrix.iloc[:, 0]
    retention_matrix = cohort_matrix.divide(cohort_sizes, axis=0) * 100
    retention_matrix = retention_matrix.round(1)

    # Clean Cohort Matrix labels for JSON export
    cohort_matrix_json = []
    for month in cohort_matrix.index:
        month_str = str(month)
        size = int(cohort_sizes[month])
        ret_vals = []
        # Support up to 12 cohort months for display
        for col in range(1, 13):
            val = retention_matrix.loc[month, col] if col in retention_matrix.columns else None
            ret_vals.append(None if pd.isna(val) else float(val))
        cohort_matrix_json.append({
            "cohort": month_str,
            "size": size,
            "retention": ret_vals
        })

    # 5. Core Performance KPIs
    total_sales = float(df_sales['TotalSpend'].sum())
    total_customers = int(df_sales['CustomerID'].nunique())
    total_orders = int(df_sales['InvoiceNo'].nunique())
    avg_order_value = round(total_sales / total_orders, 2)
    
    # Average retention rate (average of Month 2 retention across cohorts)
    # We select index 2 of retention (CohortIndex=2)
    m2_retention = retention_matrix[2].dropna()
    avg_retention_m2 = round(m2_retention.mean(), 1) if not m2_retention.empty else 0.0

    # 6. Monthly Sales Trend
    monthly_trend = df_sales.groupby('InvoiceMonth').agg({
        'TotalSpend': 'sum',
        'InvoiceNo': 'nunique'
    }).reset_index()
    monthly_trend['InvoiceMonth'] = monthly_trend['InvoiceMonth'].astype(str)
    
    sales_trend_data = []
    for _, row in monthly_trend.iterrows():
        sales_trend_data.append({
            "month": row['InvoiceMonth'],
            "revenue": round(float(row['TotalSpend']), 2),
            "orders": int(row['InvoiceNo'])
        })

    # 7. Customer Segments distribution
    segment_counts = rfm['Segment'].value_counts()
    segment_distribution = []
    for seg, count in segment_counts.items():
        segment_distribution.append({
            "segment": seg,
            "count": int(count),
            "percentage": round(float(count / total_customers * 100), 1)
        })

    # 8. Top Customers Table (to show in dashboard search table)
    top_customers = rfm.sort_values(by='Monetary', ascending=False).head(150)
    customer_list = []
    for _, row in top_customers.iterrows():
        customer_list.append({
            "id": str(row['CustomerID']),
            "recency": int(row['Recency']),
            "frequency": int(row['Frequency']),
            "monetary": round(float(row['Monetary']), 2),
            "r_score": int(row['R_Score']),
            "f_score": int(row['F_Score']),
            "m_score": int(row['M_Score']),
            "segment": row['Segment']
        })

    # Package dashboard payload
    payload = {
        "kpis": {
            "totalRevenue": total_sales,
            "totalCustomers": total_customers,
            "totalOrders": total_orders,
            "aov": avg_order_value,
            "retentionRate": avg_retention_m2
        },
        "salesTrend": sales_trend_data,
        "segmentation": segment_distribution,
        "cohorts": cohort_matrix_json,
        "customers": customer_list
    }

    # Save to data directory
    output_json_path = os.path.join("data", "dashboard_data.json")
    with open(output_json_path, 'w') as f:
        json.dump(payload, f, indent=2)

    print(f"Data Pipeline run completed successfully!")
    print(f"Dashboard metrics saved to {output_json_path}")
    print(f"Total Revenue: ${total_sales:,.2f}")
    print(f"Total Customers Analyzed: {total_customers}")
    print(f"Average Order Value: ${avg_order_value:.2f}")

if __name__ == "__main__":
    run_pipeline()
