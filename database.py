import sqlite3
from datetime import datetime

DB_NAME = "money_manager.db"

# Function to get the database connection
# Returns a new connection to the SQLite database.
# Use 'with get_connection()' to ensure automatic closing.
def get_connection():
    return sqlite3.connect(DB_NAME)

def initialize_db():
    """
    Initialize the database and create the table if it doesn't exist.
    This function is called at the start to ensure the database is set up correctly.
    """
    create_table()  # This ensures the 'transactions' table is created.

def create_table():
    """
    Creates the transactions table if it doesn't exist already.
    The table stores transaction details like type, amount, name, category, and date.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                name TEXT NOT NULL,
                category TEXT,
                date TEXT NOT NULL
            )
        ''')
        conn.commit()

def insert_transaction(trans_type, amount, name, category):
    """
    Inserts a new income or expense transaction into the database.
    The date is stored in "Month Day, Year" format 
    Args:
        trans_type (str): The type of transaction, either 'income' or 'expense'.
        amount (float): The amount of the transaction.
        name (str): The name of the transaction.
        category (str): The category of the transaction.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(''' 
            INSERT INTO transactions (type, amount, name, category, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (trans_type, amount, name, category, datetime.now().strftime("%B %d, %Y")))
        conn.commit()

def fetch_transactions():
    """
    Fetches all transactions from the database, ordered by the transaction date in descending order.
    
    Returns:
        List of dictionaries: Each dictionary represents a transaction with keys 'id', 'type', 'amount', 'name', 'category', 'date'.
    """
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row  # Ensures results are returned as dictionaries
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions ORDER BY date DESC')
        return [dict(row) for row in cursor.fetchall()]

def update_transaction_by_id(trans_id, new_name=None, new_amount=None, new_category=None):
    """
    Updates a transaction by ID. Only updates fields provided (name, amount, category).
    
    Args:
        trans_id (int): The ID of the transaction to update.
        new_name (str, optional): The new name of the transaction.
        new_amount (float, optional): The new amount of the transaction.
        new_category (str, optional): The new category of the transaction.
    
    Returns:
        bool: True if the update was successful, False otherwise.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        update_fields = []  # List to store SQL set clauses
        values = []  # List to store the new values to bind to the query

        if new_name:
            update_fields.append("name = ?")
            values.append(new_name)
        if new_amount:
            update_fields.append("amount = ?")
            values.append(float(new_amount))
        if new_category:
            update_fields.append("category = ?")
            values.append(new_category)

        if not update_fields:
            return False  # No updates to perform

        values.append(trans_id)  # Add trans_id to values for WHERE clause
        sql = f"UPDATE transactions SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(sql, values)
        conn.commit()
        return cursor.rowcount > 0  # Return True if rows were updated

def delete_transaction_by_id(trans_id):
    """
    Deletes a transaction by its ID.
    
    Args:
        trans_id (int): The ID of the transaction to delete.
    
    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
        conn.commit()
        return cursor.rowcount > 0  # Return True if a row was deleted

def get_transactions():
    """
    Fetches all transactions from the database, ordered by the transaction date in descending order.
    
    Returns:
        List of dictionaries: Each dictionary represents a transaction with keys 'id', 'type', 'amount', 'name', 'category', 'date'.
    """
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row  # Ensures results are returned as dictionaries
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions ORDER BY date DESC')
        return [dict(row) for row in cursor.fetchall()]