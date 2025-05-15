from tkinter import *
from collections import defaultdict
from datetime import datetime
from database import (
    insert_transaction, fetch_transactions, delete_transaction_by_id,
    update_transaction_by_id, get_transactions
)

class MoneyManager:

    def __init__(self, root):
        self.root = root

    def add_income(self, amount, name, category):
        # Add an income transaction to the database
        insert_transaction('income', amount, name, category)

    def add_expense(self, amount, name, category):
        # Add an expense transaction to the database
        insert_transaction('expense', amount, name, category)

    def get_transactions(self):
        # Retrieve all transactions from the database
        return fetch_transactions()

    def get_balance(self):
        # Calculate current balance by summing income and subtracting expenses
        transactions = self.get_transactions()
        income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        return income - expenses

    def refresh_transaction_log(self):
        """Refresh the transaction log list widget from the database."""
        transactions = get_transactions()  # Fetch transactions directly from DB
        self.transaction_log.delete(0, END)  # Clear previous entries

        # Loop through each transaction and display in list format
        for t in transactions:
            self.transaction_log.insert(END, f"{t['date']} | {t['type']} | {t['amount']} | {t['name']}")


    # def view_transactions(self):
    #     """
    #     Print all transactions to the console in a formatted table.
    #     Useful for debugging or CLI-based display.
    #     """
    #     transactions = self.get_transactions()
    #     if not transactions:
    #         print("No transactions recorded yet.")
    #         return

    #     for t in transactions:
    #         print(f"ID {t['id']:3} | {t['date']} | "
    #               f"{t['type'].capitalize():7} | "
    #               f"{t['name']:15} | "
    #               f"{t['category']:10} | "
    #               f"${t['amount']:.2f}")

    def edit_transaction(self, trans_id, new_name=None, new_amount=None, new_category=None):
        """
        Edit an existing transaction by ID.
        Only provided fields (name, amount, category) will be updated.
        """
        return update_transaction_by_id(trans_id, new_name, new_amount, new_category)

    def delete_transaction(self, trans_id):
        """
        Delete a transaction by its ID.
        """
        return delete_transaction_by_id(trans_id)

    def get_expense_by_category(self):
        """
        Calculate the total expenses per category.
        Only expense transactions are considered.
        """
        transactions = self.get_transactions()
        category_totals = defaultdict(float)
        for t in transactions:
            if t['type'] == 'expense':
                category_totals[t['category']] += t['amount']
        return dict(category_totals)

    def get_monthly_expenses(self):
        """
        Combine expenses on a per-month basis.
        Assumes date format is 'Month DD, YYYY'
        """
        transactions = self.get_transactions()
        monthly_expenses = defaultdict(float)

        for t in transactions:
            if t['type'] == 'expense':
                date_str = t.get('date')
                try:
                    # Parse the human-readable date format
                    date_obj = datetime.strptime(date_str, "%B %d, %Y")
                    # Create a key like '05-2025' for monthly grouping
                    month_key = date_obj.strftime("%m-%Y")
                    monthly_expenses[month_key] += t['amount']
                except Exception as e:
                    print(f"Skipping invalid date: {date_str} - {e}")
        return dict(sorted(monthly_expenses.items()))