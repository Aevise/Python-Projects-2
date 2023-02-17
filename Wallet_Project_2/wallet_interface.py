import tkinter
from tkinter import Toplevel
from Database import WalletDatabase
from datetime import datetime, date, timedelta
from pandas import DataFrame
from pandastable import Table
import matplotlib
import matplotlib.pyplot, matplotlib.figure
import matplotlib.backends.backend_tkagg 
#import random

RESOLUTION_WIDTH = 800
RESOLUTION_HEIGHT = 800
DEFAULT_WIDTH = 25
DEFAULT_PADX = 10
DEFAULT_PADY = 10

class WalletInterface():
    
    def __init__(self, root, verified_user_name):
        self.interface = Toplevel(master = root)
        self.interface.geometry(f"{RESOLUTION_WIDTH}x{RESOLUTION_HEIGHT}")
        self.interface.title("Welcome back!")
        self.user_name = verified_user_name
        self.database = WalletDatabase(self.user_name)
        self.transaction_type = tkinter.StringVar(value=0)
        self.transaction_category = tkinter.StringVar(value=0)
        self.__account_balance = 0.0
        self.transactions_today = 0
        self.history_created = False
        self.categories = ["Groceries", "Rent", "Leisure", "Insurance", "Energy", "Transportation"]

        #BUTTONS
        self.add_transaction_button = tkinter.Button(self.interface, text="Add Transaction", command=self.open_transaction_window, padx= DEFAULT_PADX, pady=DEFAULT_PADY)
        self.add_transaction_button.grid(row=0, column=2)

        self.history_button = tkinter.Button(self.interface, text="Show Transaction History", command=self.open_history_window, padx= DEFAULT_PADX, pady=DEFAULT_PADY)
        self.history_button.grid(row=0, column=3)

        self.preferences_button = tkinter.Button(self.interface, text= "Edit Preferences", command = self.open_preference_window, padx= DEFAULT_PADX, pady=DEFAULT_PADY)
        self.preferences_button.grid(row=0, column=4)

        self.show_balance = tkinter.Button(self.interface, text="Plot Balance", command=self.plot_chart, padx= DEFAULT_PADX, pady=DEFAULT_PADY)
        self.show_balance.grid(row=4, column=0)

        #LABELS
        self.account_balance_label = tkinter.Label(self.interface, text=f"Current Account Balance: {str(self.__account_balance)}")
        self.account_balance_label.grid(row=1, column=0)

        #LABEL FRAME
        self.last_days_frame = tkinter.LabelFrame(self.interface, text="Last 30 days:", pady= DEFAULT_PADY)
        self.last_days_frame.grid(row=2,column=0)

        self.limits_frame = tkinter.LabelFrame(self.interface, text="Set Limits:", pady= DEFAULT_PADY)
        self.limits_frame.grid(row=3,column=0)

        #LABELS IN FRAME LAST DAYS
        self.income_label = tkinter.Label(self.last_days_frame, text=f"Income: {self.last_income()} $ ")
        self.income_label.pack()

        self.expenses_label = tkinter.Label(self.last_days_frame, text=f"Expenses: {self.last_expenses()} $")
        self.expenses_label.pack()

        #LABELS IN FRAME LIMITS
        self.groceries_frame_label = tkinter.Label(self.limits_frame)
        self.groceries_frame_label.pack()

        self.rent_frame_label = tkinter.Label(self.limits_frame)
        self.rent_frame_label.pack()

        self.leisure_frame_label = tkinter.Label(self.limits_frame)
        self.leisure_frame_label.pack()

        self.insurance_frame_label = tkinter.Label(self.limits_frame)
        self.insurance_frame_label.pack()

        self.energy_frame_label = tkinter.Label(self.limits_frame)
        self.energy_frame_label.pack()

        self.transportation_frame_label = tkinter.Label(self.limits_frame)
        self.transportation_frame_label.pack()

        self.__update_balance()
        self.update_preference_labels()

    def open_preference_window(self):
        self.preference_window = Toplevel(self.interface)
        self.preference_window.title("Edit Preferences")
        self.settings = self.database.read_preferences()

        #LABELS
        self.groceries_label = tkinter.Label(self.preference_window, text = "Groceries:")
        self.groceries_label.grid(row=0, column=0)

        self.rent_label = tkinter.Label(self.preference_window, text="Rent: ")
        self.rent_label.grid(row=1, column=0)

        self.leisure_label = tkinter.Label(self.preference_window, text="Leisure: ")
        self.leisure_label.grid(row=2, column=0)        

        self.insurance_label = tkinter.Label(self.preference_window, text="Insurance: ")
        self.insurance_label.grid(row=3, column=0)       

        self.energy_label = tkinter.Label(self.preference_window, text="Energy: ")
        self.energy_label.grid(row=4, column=0)     

        self.transportation_label = tkinter.Label(self.preference_window, text="Transportation: ")
        self.transportation_label.grid(row=5, column=0)     
                 
        #ENTRIES
        self.groceries_entry = tkinter.Entry(self.preference_window, text = "Groceries:")
        self.groceries_entry.grid(row=0, column=1)
        self.groceries_entry.delete(0, tkinter.END)
        self.groceries_entry.insert(0, str(self.settings[0][1]))

        self.rent_entry = tkinter.Entry(self.preference_window, text="Rent: ")
        self.rent_entry.grid(row=1, column=1)
        self.rent_entry.delete(0, tkinter.END)
        self.rent_entry.insert(0, str(self.settings[0][2]))

        self.leisure_entry = tkinter.Entry(self.preference_window, text="Leisure: ")
        self.leisure_entry.grid(row=2, column=1)   
        self.leisure_entry.delete(0, tkinter.END)
        self.leisure_entry.insert(0, str(self.settings[0][3]))     

        self.insurance_entry = tkinter.Entry(self.preference_window, text="Insurance: ")
        self.insurance_entry.grid(row=3, column=1)   
        self.insurance_entry.delete(0, tkinter.END)
        self.insurance_entry.insert(0, str(self.settings[0][4]))    

        self.energy_entry = tkinter.Entry(self.preference_window, text="Energy: ")
        self.energy_entry.grid(row=4, column=1)    
        self.energy_entry.delete(0, tkinter.END)
        self.energy_entry.insert(0, str(self.settings[0][5])) 

        self.transportation_entry = tkinter.Entry(self.preference_window, text="Transportation: ")
        self.transportation_entry.grid(row=5, column=1)  
        self.transportation_entry.delete(0, tkinter.END)
        self.transportation_entry.insert(0, str(self.settings[0][6]))   

        #BUTTONS
        self.set_settings_button = tkinter.Button(self.preference_window, text="Accept Changes", command=self.change_preferences)
        self.set_settings_button.grid(row=6, column=0, columnspan=2)   

    def change_preferences(self):
        new_preferences = [
            self.user_name,
            self.groceries_entry.get(), 
            self.rent_entry.get(), 
            self.leisure_entry.get(),
            self.insurance_entry.get(),
            self.energy_entry.get(),
            self.transportation_entry.get()
            ]
        self.database.change_settings(new_preferences)
        self.update_preference_labels()

    def __update_balance(self):
        money = 0.0
        data = self.database.read_database(self.user_name)
        for transaction in data:
            money += float(transaction[6])
        self.__account_balance = money
        self.account_balance_label["text"] = f"Current Account Balance: {str(self.__account_balance)}"
        self.income_label["text"] = f"Income: {self.last_income()} $ "
        self.expenses_label["text"]=f"Expenses: {self.last_expenses()} $"

    def last_expenses(self, period=30):
        now = (date.today()-timedelta(days=30)).isoformat()
        expenses = 0
        data = self.database.read_database(self.user_name)
        for transaction in data:
            if transaction[2] > now and transaction[1] == "Send":
                expenses -= float(transaction[6])
        return expenses

    def last_income(self, period=30):
        now = (date.today()-timedelta(days=30)).isoformat()
        income = 0
        data = self.database.read_database(self.user_name)
        for transaction in data:
            if transaction[2] > now and transaction[1] == "Receive":
                income += float(transaction[6])
        return income        

    def open_transaction_window(self):
        self.transaction_window = Toplevel(self.interface)
        self.transaction_window.title("Add New Transaction")

        #RADIOBUTTON
        self.transaction_radiobutton1 = tkinter.Radiobutton(self.transaction_window, text="Receive", variable=self.transaction_type, value="Receive")
        self.transaction_radiobutton1.grid(row=0, column=1)

        self.transaction_radiobutton2 = tkinter.Radiobutton(self.transaction_window, text="Send", variable=self.transaction_type, value="Send")
        self.transaction_radiobutton2.grid(row=0, column=2)

        self.groceries_radiobutton = tkinter.Radiobutton(self.transaction_window, text = self.categories[0], variable=self.transaction_category, value=self.categories[0])
        self.groceries_radiobutton.grid(row=6, column = 0)

        self.rent_radiobutton = tkinter.Radiobutton(self.transaction_window, text = self.categories[1], variable=self.transaction_category, value=self.categories[1])
        self.rent_radiobutton.grid(row=6, column = 1)

        self.leisure_radiobutton = tkinter.Radiobutton(self.transaction_window, text = self.categories[2], variable=self.transaction_category, value=self.categories[2])
        self.leisure_radiobutton.grid(row=6, column = 2)

        self.insurance_radiobutton = tkinter.Radiobutton(self.transaction_window, text = self.categories[3], variable=self.transaction_category, value=self.categories[3])
        self.insurance_radiobutton.grid(row=7, column = 0)

        self.energy_radiobutton = tkinter.Radiobutton(self.transaction_window, text = self.categories[4], variable=self.transaction_category, value=self.categories[4])
        self.energy_radiobutton.grid(row=7, column = 1)

        self.transportation_radiobutton = tkinter.Radiobutton(self.transaction_window, text = self.categories[5], variable=self.transaction_category, value=self.categories[5])
        self.transportation_radiobutton.grid(row=7, column = 2)

        #LABELS
        self.transaction_label = tkinter.Label(self.transaction_window, text="Choose transaction type: ", justify=tkinter.LEFT)
        self.transaction_label.grid(row=0, column=0)

        self.title_label = tkinter.Label(self.transaction_window, text="Title")
        self.title_label.grid(row=2, column=0)

        self.sender_label = tkinter.Label(self.transaction_window, text="Recipient")
        self.sender_label.grid(row=3, column=0)

        self.address_label = tkinter.Label(self.transaction_window, text="Address")
        self.address_label.grid(row=4, column=0)

        self.money_label = tkinter.Label(self.transaction_window, text="Amount of Money: ")
        self.money_label.grid(row=5, column=0)

        self.category_label = tkinter.Label(self.transaction_window, text="Choose Transaction Category: ")
        self.category_label.grid(row = 8, column = 1)

        self.information_label = tkinter.Label(self.transaction_window, text=" ")
        self.information_label.grid(row=9, column=0, columnspan=2)

        #Entries
        self.title_entry = tkinter.Entry(self.transaction_window, width=DEFAULT_WIDTH)
        self.title_entry.grid(row=2, column=1)

        self.recipient_entry = tkinter.Entry(self.transaction_window, width=DEFAULT_WIDTH)
        self.recipient_entry.grid(row=3, column=1)
        
        self.address_entry = tkinter.Entry(self.transaction_window, width=DEFAULT_WIDTH)
        self.address_entry.grid(row=4, column=1)

        self.money_entry = tkinter.Entry(self.transaction_window, width=DEFAULT_WIDTH)
        self.money_entry.grid(row=5, column=1)

        #Button
        self.accept_button = tkinter.Button(self.transaction_window, text="Accept",command=self.commit_transaction)
        self.accept_button.grid(row=10, column=1)

        self.cancel_button = tkinter.Button(self.transaction_window, text="Cancel", command=self.close_transaction_window)
        self.cancel_button.grid(row=10, column=0)

    def verify_transaction_data(self, data):
        for item in data:
            if not item:
                return False
        if str(data[6]).isdigit():
            if data[1] == "Send" and float(data[6]) > self.__account_balance:
                self.information_label["text"] = f"Operation nr {self.transactions_today} failed. You don't have enough funds on your account."
                return False
            return True
        else:
            return False
    
    def withdraw_failsafe(self, transaction_type, money):
        if transaction_type == "Send":
            return str(-float(money))
        else: 
            return money

    def commit_transaction(self):
        data = [self.user_name, self.transaction_type.get(), datetime.now().strftime("%Y-%m-%d"), self.title_entry.get(), self.recipient_entry.get(), self.address_entry.get(), self.money_entry.get(), self.transaction_category.get()]
        if data[1] == "Receive":
            data[-1] = "Income"
        if self.verify_transaction_data(data):  
            data[6] = self.withdraw_failsafe(data[1], data[6])
            self.database.add_transaction(data)
            self.__update_balance()
            self.update_preference_labels()
            self.information_label["text"] = f"Operation nr {self.transactions_today} successful"
            self.transactions_today += 1
        else:
            "something has gone wrong"

    def open_history_window(self):
        self.history_window = Toplevel(self.interface)
        self.history_window.title("Transaction History")
        self.__create_transaction_history(self.history_window)

    def __create_transaction_history(self, root):
        data = self.database.read_database(self.user_name)
        pdata = DataFrame(data, columns=[
            'User',
            'Transaction Type',
            'Date',
            'Title',
            'Recipient',
            'Address',
            'Money',
            'Category'            
        ])
        #TABLE
        self.history_table = Table(root, dataframe = pdata)
        self.history_table.show()

    def calculate_expenses(self):
        data = self.database.read_database(self.user_name)
        expenses = []
        money = 0
        for transaction_type in self.categories:
            for item in data:
                if item[7] == transaction_type:
                    money -= float(item[6])
            expenses.append(money)
            money = 0
        return expenses

    def update_preference_labels(self):
        data = self.database.read_preferences()
        expenses = self.calculate_expenses()
        self.groceries_frame_label["text"] = f"Groceries: {expenses[0]} $ out of {data[0][1]} $"
        self.rent_frame_label["text"] = f"Rent: {expenses[1]} $ out of {data[0][2]} $"
        self.leisure_frame_label["text"] = f"Leisure: {expenses[2]} $ out of {data[0][3]} $"
        self.insurance_frame_label["text"] = f"Insurance: {expenses[3]} $ out of {data[0][4]} $"
        self.energy_frame_label["text"] = f"Energy: {expenses[4]} $ out of {data[0][5]} $"
        self.transportation_frame_label["text"] = f"Transportation: {expenses[5]} $ out of {data[0][6]} $"   

    def close_transaction_window(self):
        self.transaction_window.destroy()

#    def add_test_data(self):
#        past = (date.today()-timedelta(days=29))
#        data = ["test", "Receive", past, "test", "test", "test", 500, "Income"]
#        self.database.add_transaction(data)
#        for x in range(29):
#            data = ["test", "Send", past, "test", "test", "test", random.randint(-15,-5), random.choice(self.categories)]
#            self.database.add_transaction(data)
#            past += timedelta(days=1)
#        print(self.database.read_database(self.user_name))

    def plot_chart(self):
        data = self.database.read_database(self.user_name)
        #CANVAS
        income = 0
        expense = 0
        for item in data:
            current_item = list(item)
            if float(current_item[6]) < 0:
                current_item[6] = -float(item[6])
            if current_item[7] != "Income":
                expense += float(current_item[6])
            else:
                income += float(current_item[6])
            
        #fig = matplotlib.pyplot.figure(figsize=(10,5))

        self.fig2 = matplotlib.figure.Figure(figsize=(5,5), dpi=100)

        self.balance_canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.fig2, master=self.interface)    
        self.plot_balace = self.balance_canvas.get_tk_widget()
        matplotlib.pyplot.bar(["income", "expense"], [income, expense], color="maroon", width=0.3)

        matplotlib.pyplot.xlabel("General Operations")
        matplotlib.pyplot.ylabel("Money")
        matplotlib.pyplot.title("Summary of last month")
        #self.plot_balace.grid(row=6, column = 1)
        self.fig2.canvas.draw()
       # self.balance_canvas.get_tk_widget().place()

        matplotlib.pyplot.show()