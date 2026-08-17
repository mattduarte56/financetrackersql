import pandas as pd
import matplotlib.pyplot as plt
from db import engine

query = """
    SELECT t.Amount, c.Name AS Category, t.TransactionDate
    FROM Transactions t
    JOIN Categories c ON t.CategoryId = c.CategoryId
"""
df = pd.read_sql(query, engine, parse_dates=["TransactionDate"])

# --- Summary numbers ---
total_income = df[df["Amount"] > 0]["Amount"].sum()
total_expenses = df[df["Amount"] < 0]["Amount"].sum()
print(f"Total income:   ${total_income:,.2f}")
print(f"Total expenses: ${total_expenses:,.2f}")
print(f"Net:            ${total_income + total_expenses:,.2f}")

# --- Spending by category (expenses only) ---
expenses = df[df["Amount"] < 0].copy()
expenses["Amount"] = expenses["Amount"].abs()
by_category = expenses.groupby("Category")["Amount"].sum().sort_values(ascending=False)

plt.figure(figsize=(8, 5))
by_category.plot(kind="bar", color="steelblue")
plt.title("Spending by Category")
plt.ylabel("Total Spent ($)")
plt.xlabel("")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("spending_by_category.png")
plt.show()

# --- Monthly trend (income vs expenses) ---
df["Month"] = df["TransactionDate"].dt.to_period("M")
monthly = df.groupby(["Month", df["Amount"] > 0])["Amount"].sum().unstack()
monthly.columns = ["Expenses", "Income"]
monthly["Expenses"] = monthly["Expenses"].abs()

plt.figure(figsize=(8, 5))
monthly.plot(kind="bar")
plt.title("Monthly Income vs Expenses")
plt.ylabel("$")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("monthly_trend.png")
plt.show()

# --- Category share (pie chart) ---
plt.figure(figsize=(6, 6))
by_category.plot(kind="pie", autopct="%1.1f%%")
plt.title("Category Share of Spending")
plt.ylabel("")
plt.tight_layout()
plt.savefig("category_pie.png")
plt.show()