import pandas as pd
import json

# Read the Excel file
df = pd.read_excel('../data/Functions & Skills.xlsx')

print("Column names:")
print(df.columns.tolist())
print("\nFirst few rows:")
print(df.head())
print(f"\nTotal rows: {len(df)}")

# Save as JSON for easy use
skills_data = df.to_dict('records')
with open('../data/skills_taxonomy.json', 'w') as f:
    json.dump(skills_data, f, indent=2)

print("\n✓ Saved to skills_taxonomy.json")