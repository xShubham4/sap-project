# DataGuard — Automated Data Quality & Anomaly Detection Pipeline

DataGuard is an automated system for loading CSV datasets, running automated data quality checks, detecting anomalies using statistical methods (Z-Score, IQR) and Machine Learning (Isolation Forest), storing results in a local SQLite database, and visualizing everything in an interactive Streamlit dashboard.

## Setup

Set up a virtual environment and install the requirements:

```bash
cd dataguard
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate # Unix/macOS
pip install -r requirements.txt
pip install -e .
```

## Generate Sample Data

Run the generator script to create a dummy CSV file populated with deliberate anomalies, missing values, and duplicates:
```bash
python generate_sample.py
```
This generates `data/sample_orders.csv`.

## Run the Pipeline

Run the automated data quality anomaly checks using the CLI command:
```bash
dataguard --input-file data/sample_orders.csv --run-name demo_run_1
```
This will insert the quality scans into `data/warehouse/dataguard.db`.

## View the Dashboard

Start the Streamlit dashboard to interact with the results:
```bash
streamlit run app.py
```