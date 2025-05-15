from gui_app import MoneyManagerApp
from database import initialize_db

def main():
    # Initialize the database (create tables if they don't exist)
    initialize_db()  
    # Start the GUI
    app = MoneyManagerApp()  
    app.mainloop()

if __name__ == "__main__":
    main()  