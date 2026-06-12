# Apex Analytics: E-Commerce Customer Segmentation & Retention Dashboard

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-darkblue.svg)](https://pandas.pydata.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

An end-to-end data analytics and business intelligence project demonstrating data cleansing, **RFM (Recency, Frequency, Monetary) Customer Segmentation**, and **Monthly Cohort Retention Analysis**. It features a python processing pipeline, an Exploratory Data Analysis (EDA) notebook, and a premium **Interactive Web Dashboard** deployable to GitHub Pages.

🚀 **[Live Interactive Dashboard Demo](https://sommmm-py.github.io/ecommerce-rfm-segmentation-analytics/dashboard/index.html)**

---

## 📊 Business Case & Insights
In e-commerce, retaining existing customers is significantly cheaper than acquiring new ones. This project provides retail managers with:
- **RFM Customer Segmentation:** Classifies customer behavior into actionable groups (e.g., Champions, Loyal, At Risk) to run targeted marketing campaigns.
- **Cohort Retention Matrix:** Identifies the percentage of customers returning month-after-month, indicating long-term customer loyalty and product-market fit.
- **Interactive Metrics Explorer:** Allows sales teams to search and filter customer profiles by behavioral tiers.

---

## 🛠️ Tech Stack & Concepts
- **Data Engineering & Analysis:** Python, Pandas, NumPy
- **Exploratory Visualization:** Jupyter Notebook, Seaborn, Matplotlib
- **Web Dashboard:** HTML5, Vanilla CSS (Premium Glassmorphism & Dark Theme), Javascript ES6, Chart.js (Dual Y-Axis Trend & Segment distribution)
- **Deployment:** GitHub Pages

---

## 📁 Repository Structure
```text
├── data/
│   ├── raw_transactions.csv       # Raw retail transactions dataset
│   └── dashboard_data.json        # Cleaned metrics exported by python pipeline
├── dashboard/
│   ├── index.html                 # Main dashboard UI
│   ├── styles.css                 # Glassmorphism styling and themes
│   └── app.js                     # Fetch, chart render, and table search logic
├── requirements.txt               # Python package dependencies
├── generate_data.py               # Generates sample transactional data
├── data_pipeline.py               # ETL pipeline: RFM scoring & Cohort extraction
└── eda_notebook.ipynb             # Exploratory Data Analysis Notebook
```

---

## 🚀 Installation & Local Execution

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/data-analyst-portfolio-project.git
cd data-analyst-portfolio-project
```

### 2. Setup Python Environment & Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate Transactions Data & Run Pipeline
To populate the database and generate raw and processed transactional data, execute:
```bash
# Generate sample raw dataset
python generate_data.py

# Run ETL pipeline (data cleaning, RFM classification, and Cohort extraction)
python data_pipeline.py
```

### 4. Launch the Dashboard
Because the dashboard fetches metrics from a local JSON file (`dashboard_data.json`), modern browsers block these requests when opening `index.html` via double-click due to CORS security policies. 

To run it locally, start a local server:
```bash
# Using Node.js (recommended)
npx serve dashboard

# OR using Python
python -m http.server 8000 --directory dashboard
```
Then visit `http://localhost:3000` (or `http://localhost:8000`) in your browser.

---

## 📈 Analysis Methodology

### RFM Segmentation Formula
1. **Recency (R):** Number of days since the customer's last invoice date.
2. **Frequency (F):** Total number of unique invoices (transactions) made by the customer.
3. **Monetary (M):** Total monetary value spent by the customer.

Each customer is assigned a score from 1 to 5 using pandas quantiles (`qcut`), and classified as follows:
- **Champions:** Bought recently, buy often, and spend the most (R: 4-5, F: 4-5)
- **Loyal Customers:** Frequent buyers with steady spending habits (R: 3-5, F: 3-5)
- **Promising/New:** Recent buyers but low transaction frequency (R: 3-5, F: 1-2)
- **At Risk:** High-value customers who haven't purchased in a while (R: 1-2, F: 3-5)
- **Lost/Hibernating:** Low recency, low frequency, low monetary spend (R: 1-2, F: 1-2)

### Cohort Retention Formula
Customers are grouped into monthly cohorts based on the date of their **first transaction**. The retention rate for Month $N$ is calculated as:
$$\text{Retention Rate (Month } N) = \frac{\text{Active Customers in Cohort in Month } N}{\text{Total Customers who Joined in that Cohort}} \times 100$$
This is visualized as a heatmap grid on the dashboard.

---

## 🛡️ License
This project is licensed under the MIT License - see the LICENSE file for details.
