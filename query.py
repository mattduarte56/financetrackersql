import pandas as pd
from db import engine

query = """
    SELECT t.TransactionId, a.Name AS Account, c.Name AS Category,
           t.Amount, t.Description, t.TransactionDate
    FROM Transactions t
    JOIN Accounts a ON t.AccountId = a.AccountId
    JOIN Categories c ON t.CategoryId = c.CategoryId
    ORDER BY t.TransactionDate
"""

df = pd.read_sql(query, engine, parse_dates=["TransactionDate"])

pd.set_option("display.max_rows", None)      # don't truncate with "..."
pd.set_option("display.width", None)         # don't wrap columns

print(df)
print(f"\nTotal transactions: {len(df)}")