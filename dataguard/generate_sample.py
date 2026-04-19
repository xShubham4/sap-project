import pandas as pd
import numpy as np

def generate_sample_data(num_rows=1000):
    np.random.seed(42)
    # Base data
    data = {
        'order_id': np.arange(1, num_rows + 1),
        'customer_id': np.random.randint(1000, 9999, size=num_rows),
        'quantity': np.random.randint(1, 10, size=num_rows),
        'unit_price': np.round(np.random.uniform(10.0, 100.0, size=num_rows), 2),
        'status': np.random.choice(['completed', 'pending', 'cancelled'], size=num_rows),
        'timestamp': pd.date_range(start='2026-04-01', periods=num_rows, freq='h'),
    }

    df = pd.DataFrame(data)

    # Inject missing values (5%)
    missing_indices = np.random.choice(df.index, size=int(num_rows * 0.05), replace=False)
    df.loc[missing_indices, 'quantity'] = np.nan
    df.loc[np.random.choice(df.index, size=int(num_rows * 0.05), replace=False), 'unit_price'] = np.nan

    # Inject duplicates (2%)
    duplicate_indices = np.random.choice(df.index, size=int(num_rows * 0.02), replace=False)
    df = pd.concat([df, df.loc[duplicate_indices]], ignore_index=True)

    # Inject price outliers
    outlier_indices = np.random.choice(df.index, size=5, replace=False)
    df.loc[outlier_indices, 'unit_price'] = 99999.0

    # Inject negative quantities
    negative_indices = np.random.choice(df.index, size=10, replace=False)
    df.loc[negative_indices, 'quantity'] = -5

    # Ensure data dir exists
    import os
    os.makedirs('data', exist_ok=True)
    
    df.to_csv('data/sample_orders.csv', index=False)
    print(f"Generated {len(df)} sample rows to data/sample_orders.csv with intentional errors.")

if __name__ == "__main__":
    generate_sample_data()