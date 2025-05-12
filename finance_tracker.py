import streamlit as st
import pandas as pd
import csv
from datetime import datetime
import matplotlib.pyplot as plt

# Constants
CSV_FILE = "finance_data.csv"
COLUMNS = ["Date", "amount", "category", "description"]
FORMAT = "%d-%m-%Y"

# Initialize CSV
def initialize_csv():
    try:
        pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False)

# Add entry to CSV
def add_entry(date, amount, category, description):
    new_entry = {
        "Date": date,
        "amount": amount,
        "category": category,
        "description": description
    }
    with open(CSV_FILE, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=COLUMNS)
        writer.writerow(new_entry)

# Get transactions from CSV
def get_transactions(start_date, end_date):
    df = pd.read_csv(CSV_FILE)
    df["Date"] = pd.to_datetime(df["Date"], format=FORMAT)
    start_date = datetime.strptime(start_date, FORMAT)
    end_date = datetime.strptime(end_date, FORMAT)
    mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
    filtered_df = df.loc[mask]
    return filtered_df

# Plot transactions
def plot_transactions(df):
    df.set_index("Date", inplace=True)
    income_df = df[df["category"] == "Income"].resample("D").sum().reindex(df.index, fill_value=0)
    expense_df = df[df["category"] == "Expense"].resample("D").sum().reindex(df.index, fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(income_df.index, income_df["amount"], label="Income", color="green")
    ax.plot(expense_df.index, expense_df["amount"], label="Expense", color="red")
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount")
    ax.set_title("Daily Income and Expense")
    ax.legend()
    ax.grid(True)
    return fig

# Page: Home
def home_page():
    st.title("Welcome to Finance Tracker")
    st.write("This app allows you to track your income and expenses.")

# Page: Add Entry
def add_entry_page():
    st.title("Add Entry")
    date = st.date_input("Date")
    date_str = date.strftime(FORMAT)
    amount = st.number_input("Amount")
    category = st.selectbox("Category", ["Income", "Expense"])
    description = st.text_input("Description")
    if st.button("Add Entry"):
        add_entry(date_str, amount, category, description)
        st.success("Entry added successfully")

# Page: View Transactions
def view_transactions_page():
    st.title("View Transactions")
    start_date = st.date_input("Start Date", key="start_date")
    start_date_str = start_date.strftime(FORMAT)
    end_date = st.date_input("End Date", key="end_date")
    end_date_str = end_date.strftime(FORMAT)
    if st.button("View Transactions"):
        df = get_transactions(start_date_str, end_date_str)
        if df.empty:
            st.write("No transactions found in the given date range.")
        else:
            st.write(df.to_dict(orient="records"))
            total_income = df[df["category"] == "Income"]["amount"].sum()
            total_expense = df[df["category"] == "Expense"]["amount"].sum()
            st.write(f"Total Income: ${total_income:.2f}")
            st.write(f"Total Expense: ${total_expense:.2f}")
            st.write(f"Net Balance: ${(total_income - total_expense):.2f}")

            # Plot
            if st.checkbox("Plot transactions"):
                df["Date"] = pd.to_datetime(df["Date"])
                fig = plot_transactions(df)
                st.pyplot(fig)

# Main app
def main():
    initialize_csv()
    pages = {
        "Home": home_page,
        "Add Entry": add_entry_page,
        "View Transactions": view_transactions_page
    }
    page = st.sidebar.selectbox("Choose a page", list(pages.keys()))
    pages[page]()

if __name__ == "__main__":
    main()