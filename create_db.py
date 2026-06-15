import sqlite3
import pandas as pd
import os

db_filename = "text_to_sql.db"

# Remove any old file if it exists to start fresh
if os.path.exists(db_filename):
    os.remove(db_filename)

# Connect to SQLite (creates the file automatically)
conn = sqlite3.connect(db_filename)

# Map files to clean table names matching your schema design
tables_mapping = {
    'Data_CSV/Customers.csv': 'Customers',
    'Data_CSV/sales_order.csv': 'sales_order',
    'Data_CSV/Products.csv': 'Products',
    'Data_CSV/Regions.csv': 'Regions',
    'Data_CSV/State_Regions.csv': 'State_Regions',
    'Data_CSV/2017_Budgets.csv': 'Budgets_2017'
}

print("--- Starting Data Migration to SQLite ---")
for csv_file, table_name in tables_mapping.items():
    if os.path.exists(csv_file):
        # Load the CSV data
        df = pd.read_csv(csv_file)
        # Import directly into SQLite preserving exact column headers
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"✅ Successfully loaded '{csv_file}' into table '{table_name}' ({len(df)} rows).")
    else:
        print(f"❌ Warning: Could not find '{csv_file}' in this directory.")

conn.close()
print(f"\n🎉 Done! Created your complete local offline database: '{db_filename}'")