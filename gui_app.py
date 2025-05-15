import customtkinter as ctk
from money_manager import MoneyManager
import tkinter.messagebox as messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

class MoneyManagerApp(ctk.CTk):
    
    def __init__(self):
        super().__init__()

        self.title("Money Manager")
        self.geometry("800x700")

        self.manager = MoneyManager(self)
        self.selected_transaction_id = None  # Stores ID of selected transaction for editing/deleting

        # --- Balance Display ---
        self.balance_frame = ctk.CTkFrame(self)
        self.balance_frame.pack(pady=10, padx=20, fill="x")

        self.balance_label = ctk.CTkLabel(self.balance_frame, text="Balance: $0.00")
        self.balance_label.pack()
        self.update_balance()  # Initialize balance display

        # --- Transaction Input Fields ---
        self.transaction_frame = ctk.CTkFrame(self)
        self.transaction_frame.pack(pady=10, padx=20, fill="x")

        self.name_entry = ctk.CTkEntry(self.transaction_frame, placeholder_text="Name")
        self.name_entry.pack(pady=5, padx=10, fill="x")

        self.amount_entry = ctk.CTkEntry(self.transaction_frame, placeholder_text="Amount")
        self.amount_entry.pack(pady=5, padx=10, fill="x")

        self.category_entry = ctk.CTkEntry(self.transaction_frame, placeholder_text="Category")
        self.category_entry.pack(pady=5, padx=10, fill="x")

        # --- Buttons to Add Income or Expense ---
        self.income_button = ctk.CTkButton(self.transaction_frame, text="Add Income", command=self.add_income)
        self.income_button.pack(side="left", padx=10, pady=5)

        self.expense_button = ctk.CTkButton(self.transaction_frame, text="Add Expense", command=self.add_expense)
        self.expense_button.pack(side="left", padx=10, pady=5)

        # --- Transaction Log Display ---
        self.transaction_log_frame = ctk.CTkFrame(self)
        self.transaction_log_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.transaction_log_label = ctk.CTkLabel(self.transaction_log_frame, text="Transactions:")
        self.transaction_log_label.pack(anchor="w", padx=10)

        # Multiline textbox to show transaction list
        self.transaction_log_text = ctk.CTkTextbox(
            self.transaction_log_frame,
            height=250,
            font=("Courier", 12)  # Monospaced font for aligned layout
        )
        self.transaction_log_text.pack(padx=10, pady=10, fill="both", expand=True)
        self.transaction_log_text.bind("<Button-1>", self.select_transaction)  # Click to select transaction

        # --- Edit and Delete Buttons for Selected Transaction ---
        self.edit_button = ctk.CTkButton(self, text="Edit Selected", command=self.edit_selected_transaction)
        self.edit_button.pack(pady=5)

        self.delete_button = ctk.CTkButton(self, text="Delete Selected", command=self.delete_selected_transaction)
        self.delete_button.pack(pady=5)

        self.refresh_transaction_log()  # Initial load of transactions

        # --- Report ---
        self.report_button = ctk.CTkButton(self, text="Run Report", command=self.run_report)
        self.report_button.pack(pady=10)

    
    def add_income(self):
        self.add_transaction('income')

    
    def add_expense(self):
        self.add_transaction('expense')

    
    def add_transaction(self, type_):
        """
        Adds a new transaction (income or expense) to the database.
        Validates input, ensures valid amount, updates the balance, and refreshes the transaction log.
        """
        try:
            # Retrieve user input and strip any leading/trailing whitespace
            name = self.name_entry.get().strip()
            amount = self.amount_entry.get().strip()
            category = self.category_entry.get().strip()

            # Check if any of the required fields are empty
            if not name or not category or not amount:
                raise ValueError("One or more fields are invalid.")

            # Attempt to convert the amount to a float and validate it
            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError("Amount must be greater than zero.")
            except ValueError:
                raise ValueError("Amount must be a valid number.")  # If conversion fails, show an error message

            # Add the transaction based on its type (income or expense)
            if type_ == 'income':
                self.manager.add_income(amount, name, category)  # Call manager to add income
            else:
                self.manager.add_expense(amount, name, category)  # Call manager to add expense

            # Clear the input fields after successful transaction addition
            self.name_entry.delete(0, 'end')
            self.amount_entry.delete(0, 'end')
            self.category_entry.delete(0, 'end')

            # Update balance and refresh the transaction log to reflect changes
            self.update_balance()
            self.refresh_transaction_log()

        except ValueError as e:
            # Show an error message if there is any invalid input
            messagebox.showerror("Invalid Entry", str(e))

    
    def update_balance(self):
        balance = self.manager.get_balance()
        self.balance_label.configure(text=f"Balance: ${balance:.2f}")

    
    def refresh_transaction_log(self):
        self.transaction_log_text.configure(state="normal")
        self.transaction_log_text.delete(1.0, 'end')
        self.transactions_display_map = {}

        # Updated headings with wider columns for alignment
        headings = "{:<23}  {:<10}  {:<24}  {:>10}  {:<15}\n".format(
            "Date", "Type", "Name", "Amount", "Category"
        )
        self.transaction_log_text.insert("end", headings)
        self.transaction_log_text.insert("end", "-" * len(headings) + "\n")

        for i, transaction in enumerate(self.manager.get_transactions()):
            display_text = "{:<23}  {:<10}  {:<24}  {:>10}  {:<15}\n".format(
                transaction['date'],
                transaction['type'],
                transaction['name'],
                f"${transaction['amount']:,.2f}",  # Dollar sign included with amount
                transaction['category']
    )
            self.transaction_log_text.insert("end", display_text)
            self.transactions_display_map[i + 3] = transaction['id']

        self.transaction_log_text.configure(state="disabled")

    
    def select_transaction(self, event):
        # Enable textbox temporarily
        self.transaction_log_text.configure(state="normal")

        # Remove any existing tag highlights
        self.transaction_log_text.tag_remove("highlight", "1.0", "end")

        # Get clicked line number
        index = self.transaction_log_text.index(f"@{event.x},{event.y}")
        line = int(index.split(".")[0])
        self.selected_transaction_id = self.transactions_display_map.get(line)

        # Apply highlight tag to the selected line
        self.transaction_log_text.tag_add("highlight", f"{line}.0", f"{line}.end")
        self.transaction_log_text.tag_config("highlight", background="#d0eaff")  # You can pick any color

        # Lock the textbox again
        self.transaction_log_text.configure(state="disabled")

    
    def edit_selected_transaction(self):
        # Retrieve the selected transaction using its ID and open edit window
        if self.selected_transaction_id is None:
            return

        transaction = next((t for t in self.manager.get_transactions() if t['id'] == self.selected_transaction_id), None)
        if transaction:
            self.edit_transaction(transaction)


    def delete_selected_transaction(self):
        # Confirm and delete the selected transaction by its ID
        if self.selected_transaction_id is None:
            return

        transaction = next((t for t in self.manager.get_transactions() if t['id'] == self.selected_transaction_id), None)
        if not transaction:
            return

        # Confirmation box showing the transaction name and amount
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete '{transaction['name']}' for ${transaction['amount']:.2f}?"
        )

        if confirm:
            self.manager.delete_transaction(transaction['id'])
            self.selected_transaction_id = None
            self.update_balance()
            self.refresh_transaction_log()


    def edit_transaction(self, transaction):
        """Open a popup window for editing a transaction."""
        
        # Create a popup window
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit Transaction")
        edit_window.geometry("400x300")
        edit_window.lift()
        edit_window.grab_set()
        edit_window.focus_force()

        # Pre-fill entry fields with current transaction data
        name_entry = ctk.CTkEntry(edit_window, placeholder_text="Name")
        name_entry.insert(0, transaction['name'])
        name_entry.pack(pady=10, padx=20, fill="x")

        amount_entry = ctk.CTkEntry(edit_window, placeholder_text="Amount")
        amount_entry.insert(0, str(transaction['amount']))
        amount_entry.pack(pady=10, padx=20, fill="x")

        category_entry = ctk.CTkEntry(edit_window, placeholder_text="Category")
        category_entry.insert(0, transaction['category'])
        category_entry.pack(pady=10, padx=20, fill="x")

        # Internal function to save the changes made in the popup
        def save_changes():
            new_name = name_entry.get().strip()
            new_amount = amount_entry.get().strip()
            new_category = category_entry.get().strip()

            if not new_name or not new_category or not new_amount:
                return

            try:
                new_amount = float(new_amount)
            except ValueError:
                return

            # Update the transaction and refresh UI
            if self.manager.edit_transaction(transaction['id'], new_name, new_amount, new_category):
                self.update_balance()
                self.refresh_transaction_log()
                edit_window.destroy()
            else:
                print("Error updating transaction")

        # Save button for the popup
        save_button = ctk.CTkButton(edit_window, text="Save Changes", command=save_changes)
        save_button.pack(pady=20)

   
    def run_report(self):
        self.show_charts()


    def show_charts(self):
        import matplotlib
        matplotlib.use("Agg")  # Prevents backend conflicts when using Tkinter

        # Create a new window to display the financial charts
        report_window = ctk.CTkToplevel(self)
        report_window.title("Financial Report")
        report_window.geometry("900x700")
        report_window.attributes("-topmost", True)  # Keep window above others

        # Create a figure with two side-by-side subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
        
        # --- Pie Chart: Expenses by Category ---
        category_data = self.manager.get_expense_by_category()
        if category_data:
            ax1.pie(category_data.values(), labels=category_data.keys(), autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')  # Equal aspect ratio for a circular pie
            ax1.set_title('Expenses by Category')
        else:
            ax1.text(0.5, 0.5, 'No expense data', ha='center', va='center')
            ax1.axis('off')  # Hide axes when there's no data

        # --- Bar Chart: Monthly Expenses ---
        monthly_expenses = self.manager.get_monthly_expenses()
        print("Monthly Expenses:", monthly_expenses)  # Debugging output
        if monthly_expenses:
            months = list(monthly_expenses.keys())
            values = list(monthly_expenses.values())
            ax2.bar(months, values)
            ax2.set_title('Monthly Expenses')
            ax2.set_xlabel('Month')
            ax2.set_ylabel('Amount')
        else:
            ax2.text(0.5, 0.5, 'No monthly data', ha='center', va='center')
            ax2.axis('off')

        plt.tight_layout()  # Adjust layout to prevent overlap

        # Embed the matplotlib figure into the customTkinter window
        canvas = FigureCanvasTkAgg(fig, master=report_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Ensure matplotlib figure is closed and memory cleaned when window is closed
        def on_close():
            plt.close(fig)
            report_window.destroy()

        report_window.protocol("WM_DELETE_WINDOW", on_close)
        
        

