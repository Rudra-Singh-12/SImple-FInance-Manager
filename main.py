import pandas as pd
import csv
from datetime import datetime
from data_entry import get_date,get_amount,get_category,get_description
import matplotlib.pyplot as plt

class CSV:
    CSV_FILE="finance_data.csv"
    COLUMNS=["Date","amount","category","description"]
    FORMAT="%d-%m-%Y"

    @classmethod
    def initialize_csv(cls):
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df=pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE,index=False)
    @classmethod
    def add_entry(cls,date,amount,category,description):
        new_entry = {
            "Date": date,
            "amount": amount,
            "category": category,
            "description": description
        }
        with open(cls.CSV_FILE, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        print(f"Entry added successfully")

    @classmethod
    def get_transactions(cls,start_date,end_date):
            df=pd.read_csv(cls.CSV_FILE)
            df["Date"]=pd.to_datetime(df["Date"],format=CSV.FORMAT)
            start_date=datetime.strptime(start_date,CSV.FORMAT)
            end_date=datetime.strptime(end_date,CSV.FORMAT)
            mask=(df["Date"]>=start_date) & (df["Date"]<=end_date)
            filtered_df=df.loc[mask]

            if filtered_df.empty:
                print("No transactions found in the given date range.")
            else:
                print("Transactions from {start_date.strftime(CSV.FORMAT)} to {end_date.strftime(CSV.FORMAT)}:")
                print(filtered_df.to_string(index=False,formatters={"Date":lambda x: x.strftime(CSV.FORMAT)}))
                total_income=filtered_df[filtered_df["category"]=="Income"]["amount"].sum()
                total_expense=filtered_df[filtered_df["category"]=="Expense"]["amount"].sum()
                print("\nSummary:")
                print(f"Total Income: ${total_income:.2f}")
                print(f"Total Expense: ${total_expense:.2f}")
                print(f"Net Balance: ${(total_income - total_expense):.2f}")

def add():
    CSV.initialize_csv()
    date=get_date("Enter the date (dd-mm-yyyy): ",allow_default=True)
    amount=get_amount()
    category=get_category()
    description=get_description()
    CSV.add_entry(date,amount,category,description)

def plot_transactions(df):
    df.set_index("Date", inplace=True)  
    income_df=df[df["category"]=="Income"].resample("D").sum().reindex(df.index, fill_value=0)
    expense_df=df[df["category"]=="Expense"].resample("D").sum().reindex(df.index, fill_value=0)
    plt.figure(figsize=(10, 5))
    plt.plot(income_df.index, income_df["amount"], label="Income", color="green")
    plt.plot(expense_df.index, expense_df["amount"], label="Expense", color="red")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Daily Income and Expense")
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    while True:
        print("\n1. Add Entry")
        print("2. View Transactions")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            add()
        elif choice == '2':
            start_date = get_date("Enter start date (dd-mm-yyyy): ")
            end_date = get_date("Enter end date (dd-mm-yyyy): ")
            df=CSV.get_transactions(start_date, end_date)
            if input("Do you want to plot the transactions? (y/n): ").lower() == 'y':
                df=pd.read_csv(CSV.CSV_FILE)
                df["Date"]=pd.to_datetime(df["Date"],format=CSV.FORMAT)
                plot_transactions(df)
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()