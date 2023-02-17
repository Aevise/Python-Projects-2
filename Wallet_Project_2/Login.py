import tkinter
import os
from Database import UsersDB
from wallet_interface import WalletInterface
from tkinter import Tk

ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
RESOLUTION_WIDTH = 500
RESOLUTION_HEIGHT = 500
DEFAULT_PADX = 10
DEFAULT_PADY = 10 
TITLE = "Wallet Application Login Menu"

class Login():

    def __init__(self) -> None:
        self.login_window = Tk()
        self.database = UsersDB()
        self.login_window.title(TITLE)
        self.tries = 0
        self.wallet = None
        #login_window.iconbitmap("DO DODANIA!!")
        self.login_window.geometry(f"{RESOLUTION_WIDTH}x{RESOLUTION_HEIGHT}")

        #Text Box Labels
        self.username_label = tkinter.Label(text="Username: ")
        self.username_label.grid(row=0, column=0, pady=DEFAULT_PADY/2)

        self.password_label = tkinter.Label(text="Password: ")
        self.password_label.grid(row=1, column=0, pady=DEFAULT_PADY/2)

        self.credentials_label = tkinter.Label(text="")
        self.credentials_label.grid(row=2, column=0, columnspan=2)

        self.create_username_label = tkinter.Label(text="Username: ")

        self.crate_password_label = tkinter.Label(text="Password")

        self.crate_confirmpassword_label = tkinter.Label(text="Password")

        self.create_name_label = tkinter.Label(text="Name: ")      

        self.create_surname_label = tkinter.Label(text="Surname: ")     

        self.create_email_label = tkinter.Label(text="Email: ")     

        self.create_info_label = tkinter.Label(text="")

        #Entries
        self.username_entry = tkinter.Entry(width=50)
        self.username_entry.grid(row=0, column=1)

        self.password_entry = tkinter.Entry(width=50, show="***")
        self.password_entry.grid(row=1, column=1)

        self.create_username_entry = tkinter.Entry(width=50)

        self.crate_password_entry = tkinter.Entry(width=50, show="***")

        self.crate_confirmpassword_entry = tkinter.Entry(width=50, show="***")

        self.create_name_entry = tkinter.Entry(width=50)      

        self.create_surname_entry = tkinter.Entry(width=50)  

        self.create_email_entry = tkinter.Entry(width=50)    

        #Button
        self.forgot_pass_button = tkinter.Button(text="Forgot Password")
        self.forgot_pass_button.grid(row=3, column=0)

        self.submit_button = tkinter.Button(text="Log in", command = self.verify_user, pady=DEFAULT_PADY, width= DEFAULT_PADX*2)
        self.submit_button.grid(row = 3, column=1, pady=DEFAULT_PADY)

        self.create_account_button = tkinter.Button(text = "Sign up", pady=DEFAULT_PADY, command=self.show_user_creation)
        self.create_account_button.grid(row=4, column=0)

        self.create_account_button2 = tkinter.Button(text = 'Accept', pady=DEFAULT_PADY, command=self.add_user)

        self.login_window.mainloop()

    def add_user(self):
        user_data = [
            self.create_username_entry.get(), 
            self.crate_password_entry.get(),
            self.crate_confirmpassword_entry.get(),
            self.create_name_entry.get(),
            self.create_surname_entry.get(),
            self.create_email_entry.get()
            ]
        
        data_provided = True
        self.create_info_label.grid(row=12, column=0, columnspan=2)

        for data in user_data:
            if not data:
                data_provided = False
                self.create_info_label["text"] = "Provide all necessary data"
        if self.password_match(user_data[1], user_data[2]) and self.check_email(user_data[5]):
            if data_provided:
                if self.database.add_user(user_data):
                    self.create_info_label["text"] = "Account successfully created"
                else:
                    self.create_info_label["text"] = "Account already exist"
        else:
            self.create_info_label["text"] = "Password does not match"

    def password_match(self, pass1, pass2):
        self.tries +=1
        if self.tries > 5:
            self.create_info_label["text"] = "Too many tries, please try again later"
        else:
            if pass1 == pass2:
                return True
            else:
                return False

    def check_email(self, email):
        if "@" not in email:
            return False
        else:
            monkeylocation = email.find("@")
            if monkeylocation < email.rfind("."):
                return True
            else:
                return False

    def verify_user(self):
        if self.database.check_users_credentials(self.username_entry.get(), self.password_entry.get()):
            self.credentials_label["text"] = "Credentials correct"
            user = self.username_entry.get()
            self.wallet = WalletInterface(self.login_window, user)
        else:
            self.credentials_label["text"] = "No user with such credentials created"

    def show_user_creation(self):
        #Text Box Labels
        self.create_username_label.grid(row=5, column=0)
        self.crate_password_label.grid(row=6, column=0, pady=DEFAULT_PADY/2)
        self.crate_confirmpassword_label.grid(row=7, column=0, pady=DEFAULT_PADY/2) 
        self.create_name_label.grid(row=8, column=0, pady=DEFAULT_PADY/2)   
        self.create_surname_label.grid(row=9, column=0, pady=DEFAULT_PADY/2)  
        self.create_email_label.grid(row=10, column=0, pady=DEFAULT_PADY/2)

        #Entries
        self.create_username_entry.grid(row=5, column=1)
        self.crate_password_entry.grid(row=6, column=1)
        self.crate_confirmpassword_entry.grid(row=7, column=1) 
        self.create_name_entry.grid(row=8, column=1)
        self.create_surname_entry.grid(row=9, column=1)
        self.create_email_entry.grid(row=10, column=1)        

        self.create_account_button.grid_forget()
        self.create_account_button2.grid(row=11, column=1, columnspan=2)
