import pandas as pd
from sqlalchemy import create_engine


# PostgreSQL Connection

engine = create_engine(
    "postgresql://postgres:0415@localhost:5432/supply_chain_risk"
)


query = """
SELECT *
FROM final_risk_view;
"""


df = pd.read_sql(query, engine)


print(df.head())

print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns)

