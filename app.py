import streamlit as st
import pandas as pd
from db import engine

st.set_page_config(page_title="Finance Tracker", layout="wide")
st.title("💰 Finance Tracker")

query = """
    SELECT t.TransactionId, a.Name AS Account, c.Name AS Category,
           t.Amount, t.Description, t.TransactionDate
    FROM Transactions t
    JOIN Accounts a ON t.AccountId = a.AccountId
    JOIN Categories c ON t.CategoryId = c.CategoryId
    ORDER BY t.TransactionDate
"""
df = pd.read_sql(query, engine, parse_dates=["TransactionDate"])

# --- Summary metrics at the top ---
total_income = df[df["Amount"] > 0]["Amount"].sum()
total_expenses = df[df["Amount"] < 0]["Amount"].sum()
col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"${total_income:,.2f}")
col2.metric("Total Expenses", f"${total_expenses:,.2f}")
col3.metric("Net", f"${total_income + total_expenses:,.2f}")

# --- Filters ---
categories = ["All"] + sorted(df["Category"].unique().tolist())
selected_category = st.selectbox("Filter by category", categories)

filtered = df if selected_category == "All" else df[df["Category"] == selected_category]
st.subheader("📤 Upload Bank Statement")
uploaded_file = st.file_uploader("Upload a CSV", type="csv")

if uploaded_file is not None:
    raw = pd.read_csv(uploaded_file)
    st.write("Preview:", raw.head())

    st.markdown("**Map your CSV columns:**")
    col_date = st.selectbox("Date column", raw.columns)
    col_desc = st.selectbox("Description column", raw.columns)
    col_amount = st.selectbox("Amount column", raw.columns)

    account_name = st.text_input("Which account is this for?", "Main Checking")
    default_category = st.selectbox("Default category for these rows", 
                                     df["Category"].unique().tolist() + ["Uncategorized"])

    if st.button("Import"):
        with engine.begin() as conn:
            # Ensure account exists
            acc = conn.exec_driver_sql(
                "SELECT AccountId FROM Accounts WHERE Name = ?", (account_name,)
            ).fetchone()
            if not acc:
                conn.exec_driver_sql(
                    "INSERT INTO Accounts (Name, Type) VALUES (?, ?)", (account_name, "Checking")
                )
                acc = conn.exec_driver_sql(
                    "SELECT AccountId FROM Accounts WHERE Name = ?", (account_name,)
                ).fetchone()
            account_id = acc[0]

            # Ensure category exists
            cat = conn.exec_driver_sql(
                "SELECT CategoryId FROM Categories WHERE Name = ?", (default_category,)
            ).fetchone()
            if not cat:
                conn.exec_driver_sql(
                    "INSERT INTO Categories (Name, IsIncome) VALUES (?, ?)", (default_category, 0)
                )
                cat = conn.exec_driver_sql(
                    "SELECT CategoryId FROM Categories WHERE Name = ?", (default_category,)
                ).fetchone()
            category_id = cat[0]

            inserted = 0
            for _, row in raw.iterrows():
                # Skip if an identical transaction already exists (basic dedupe)
                exists = conn.exec_driver_sql(
                    """SELECT 1 FROM Transactions 
                       WHERE AccountId = ? AND Amount = ? AND Description = ? AND TransactionDate = ?""",
                    (account_id, row[col_amount], str(row[col_desc]), row[col_date])
                ).fetchone()
                if exists:
                    continue

                conn.exec_driver_sql(
                    """INSERT INTO Transactions (AccountId, CategoryId, Amount, Description, TransactionDate)
                       VALUES (?, ?, ?, ?, ?)""",
                    (account_id, category_id, row[col_amount], str(row[col_desc]), row[col_date])
                )
                inserted += 1

        st.success(f"Imported {inserted} new transactions ({len(raw) - inserted} skipped as duplicates).")
        st.rerun()
# --- Transactions table ---
st.subheader("Transactions")
st.dataframe(filtered, use_container_width=True)

# --- Charts ---
st.subheader("Spending by Category")
expenses = df[df["Amount"] < 0].copy()
expenses["Amount"] = expenses["Amount"].abs()
by_category = expenses.groupby("Category")["Amount"].sum().sort_values(ascending=False)
st.bar_chart(by_category)

st.subheader("Monthly Income vs Expenses")
df["Month"] = df["TransactionDate"].dt.to_period("M").astype(str)
monthly = df.groupby(["Month", df["Amount"] > 0])["Amount"].sum().unstack()
monthly.columns = ["Expenses", "Income"]
monthly["Expenses"] = monthly["Expenses"].abs()
st.bar_chart(monthly)

