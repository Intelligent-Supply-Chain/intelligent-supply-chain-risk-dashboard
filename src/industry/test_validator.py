import pandas as pd
from data_validator import validate_csv


# Create a small test dataset
test_data = pd.DataFrame({
    "part_id": ["P001", "P002", "P003", "P003"],
    "inventory": [100, None, 300, 300],
    "supplier_id": ["SUP01", "SUP02", "SUP03", "SUP03"]
})

# Save temporary CSV
test_data.to_csv("test_company_data.csv", index=False)

# Validate the CSV
df, messages = validate_csv("test_company_data.csv")

print("\n===== DATA VALIDATION TEST =====")

print("\nDataset shape:")
print(df.shape)

print("\nDataset preview:")
print(df)

print("\nValidation messages:")

if messages:
    for message in messages:
        print("⚠️", message)
else:
    print("✅ No issues found.")

print("\n===== TEST COMPLETED =====")