import streamlit as st
import pandas as pd
import csv
from datetime import datetime
import matplotlib.pyplot as plt

# CSV handling class
class CSV:
    CSV_FILE = "finance_data.csv"
    COLUMNS = ["Date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initialize_csv(cls):
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)

    @classmethod
    def add_entry(cls, date, amount, category, description):
        new_entry = {
            "Date": date,
            "amount": amount,
            "category": category,
            "description": description
        }
        with open(cls.CSV_FILE, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        st.success("✅ Entry added successfully!")

    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = pd.read_csv(cls.CSV_FILE)
        df["Date"] = pd.to_datetime(df["Date"], format=CSV.FORMAT)
        # Convert start and end date
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
        filtered_df = df.loc[mask]
        return filtered_df

# Plotting function
def plot_transactions(df):
    df.set_index("Date", inplace=True)
    income_df = df[df["category"] == "Income"].resample("D").sum().reindex(df.index, fill_value=0)
    expense_df = df[df["category"] == "Expense"].resample("D").sum().reindex(df.index, fill_value=0)

    st.line_chart(pd.DataFrame({
        "Income": income_df["amount"],
        "Expense": expense_df["amount"]
    }))

# Main Streamlit App
def main():
    st.set_page_config(page_title="Personal Finance Tracker", page_icon="💸")
    st.title("💸 Personal Finance Tracker")

    CSV.initialize_csv()

    menu = st.sidebar.selectbox("Menu", ["Add Entry", "View Transactions"])

    if menu == "Add Entry":
        st.subheader("➕ Add New Transaction")
        with st.form("entry_form"):
            date = st.date_input("Date", value=datetime.now())
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            category = st.selectbox("Category", ["Income", "Expense"])
            description = st.text_input("Description")
            submitted = st.form_submit_button("Add Transaction")
            if submitted:
                formatted_date = date.strftime(CSV.FORMAT)
                CSV.add_entry(formatted_date, amount, category, description)

    elif menu == "View Transactions":
        st.subheader("📋 View Transactions")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now().replace(day=1))
        with col2:
            end_date = st.date_input("End Date", value=datetime.now())

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        if st.button("Show Transactions"):
            df = CSV.get_transactions(start_date, end_date)

            if df.empty:
                st.warning("⚠️ No transactions found in this date range.")
            else:
                st.dataframe(df)

                total_income = df[df["category"] == "Income"]["amount"].sum()
                total_expense = df[df["category"] == "Expense"]["amount"].sum()
                net_balance = total_income - total_expense

                st.markdown("### 📊 Summary")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Income", f"${total_income:.2f}")
                col2.metric("Total Expense", f"${total_expense:.2f}")
                col3.metric("Net Balance", f"${net_balance:.2f}")

                if st.checkbox("Show Income vs Expense Chart"):
                    plot_transactions(df)

# Run the app
if __name__ == "__main__":
    main()
