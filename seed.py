import pandas as pd
from db import engine

df = pd.read_csv("transactions_seed.csv")

with engine.begin() as conn:
    # Ensure accounts exist
    for account_name in df["AccountName"].unique():
        exists = conn.exec_driver_sql(
            "SELECT AccountId FROM Accounts WHERE Name = ?", (account_name,)
        ).fetchone()
        if not exists:
            conn.exec_driver_sql(
                "INSERT INTO Accounts (Name, Type) VALUES (?, ?)", (account_name, "Checking")
            )

    # Ensure categories exist
    income_categories = {"Paycheck", "Freelance"}
    for category_name in df["CategoryName"].unique():
        exists = conn.exec_driver_sql(
            "SELECT CategoryId FROM Categories WHERE Name = ?", (category_name,)
        ).fetchone()
        if not exists:
            is_income = 1 if category_name in income_categories else 0
            conn.exec_driver_sql(
                "INSERT INTO Categories (Name, IsIncome) VALUES (?, ?)", (category_name, is_income)
            )

    # Build lookup maps
    accounts = dict(conn.exec_driver_sql("SELECT Name, AccountId FROM Accounts").fetchall())
    categories = dict(conn.exec_driver_sql("SELECT Name, CategoryId FROM Categories").fetchall())

    # Insert transactions
    for _, row in df.iterrows():
        conn.exec_driver_sql(
            """INSERT INTO Transactions (AccountId, CategoryId, Amount, Description, TransactionDate)
               VALUES (?, ?, ?, ?, ?)""",
            (
                accounts[row["AccountName"]],
                categories[row["CategoryName"]],
                row["Amount"],
                row["Description"],
                row["TransactionDate"],
            ),
        )

print(f"Loaded {len(df)} transactions.")