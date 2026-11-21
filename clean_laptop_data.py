# Cleaning script: laptopData.csv (original, unchanged) -> cleaned_laptopData.csv
# Keep this file, laptopData.csv and the output in the same folder.

import os
import pandas as pd

# 1. File paths (same folder as this script)
base_folder = os.path.dirname(os.path.abspath(__file__))
raw_path = os.path.join(base_folder, "laptopData.csv")
clean_path = os.path.join(base_folder, "cleaned_laptopData.csv")

# 2. Load the original CSV
if not os.path.exists(raw_path):
    raise SystemExit("Could not find laptopData.csv in " + base_folder)
df = pd.read_csv(raw_path)
print("Rows in original file:", len(df))

# 3. Drop the exported index column
if "Unnamed: 0" in df.columns:
    df = df.drop(columns=["Unnamed: 0"])

# 4. Remove rows that are completely blank
df = df.dropna(how="all")
print("Rows after removing blank rows:", len(df))

# 5. Remove extra spaces in text columns, then turn "?" into missing values
for column in df.columns:
    if pd.api.types.is_string_dtype(df[column]):
        df[column] = df[column].str.strip()
df = df.replace("?", float("nan"))

# 6. Make number columns from the text columns (no values are invented)
df["RAM_GB"] = pd.to_numeric(df["Ram"].str.replace("GB", "", regex=False), errors="coerce")
df["Weight_kg"] = pd.to_numeric(df["Weight"].str.replace("kg", "", regex=False), errors="coerce")
df["Inches"] = pd.to_numeric(df["Inches"], errors="coerce")

# 7. Rename Price to Price_INR (values stay exactly as supplied)
df["Price_INR"] = pd.to_numeric(df["Price"], errors="coerce")

# 8. Keep the useful columns in a clear order
#    (the old text columns Ram, Weight and Price are replaced by the numeric ones)
keep = ["Company", "TypeName", "Inches", "ScreenResolution", "Cpu", "RAM_GB",
        "Memory", "Gpu", "OpSys", "Weight_kg", "Price_INR"]
df = df[keep]

# 9. Rows that repeat are NOT removed: there is no model-name column,
#    so we cannot confirm they are really duplicate products.

# 10. Save and report missing values
df.to_csv(clean_path, index=False)
print("Saved", len(df), "rows to", clean_path)
print("Missing values per column:")
print(df.isna().sum())
