import sqlite3

DB_NAME = 'users_data'
WALLET_DB = 'wallet_data'

class UsersDB():
    
    def __init__(self) -> None:
        #Create or connect the database
        self.__connection = sqlite3.connect(f'{DB_NAME}.db')
            #Creating Cursor
        self.__cursor = self.__connection.cursor()
        #Create table
        try:
            self.__connection.execute("""CREATE TABLE users (
                username text, 
                password text,
                first_name text, 
                last_name text,
                email text)""")
            print("Database not found. Creating Database.")
        except sqlite3.OperationalError:
            print("Database found. Creating Connection.")

    def add_user(self, user_data):
        if self.user_already_created(user_data[0], user_data[5]):
            return False
        else:
            self.__cursor.execute("INSERT INTO users VALUES (:username, :password, :name, :surname, :email)",
            {
                'username':user_data[0],
                'password':user_data[1],
                'name':user_data[3],
                'surname':user_data[4],
                'email':user_data[5]
            }) 
            self.commit_changes()
            return True
        
    def __read_database(self):
        self.__cursor.execute(f"SELECT * FROM users")
        return self.__cursor.fetchall()

    def user_already_created(self, username, email):
        data = self.__read_database()
        for user in data:
            if username in user or email in user:
                return True
        return False

    def check_users_credentials(self, login, password):
        data = self.__read_database()
        for user in data:
            if login in user and password in user:
                return True
        return False

    def commit_changes(self):
        #Commit changes
        self.__connection.commit()

    def close_connection(self):
        #close connection
        self.__connection.close()


class WalletDatabase():
    def __init__(self, username) -> None:
        #Create or connect the database
        self.__user = username + "_" + WALLET_DB
        self.__connection = sqlite3.connect(f'{self.__user}.db')
            #Creating Cursor
        self.__cursor = self.__connection.cursor()
        try:
            self.__connection.execute("""CREATE TABLE wallets (
                username text, 
                transaction_type text,
                date text,
                money real, 
                title text,
                sender text,
                address text,
                category text)""")
            print("Database Wallet not found. Creating Database.")
        except sqlite3.OperationalError:
            print("Database Wallet found. Creating Connection.")

        self.__user_pref = username + "_preferences"
        self.__pref_connection = sqlite3.connect(f'{self.__user_pref}.db')
        self.__cursor2 = self.__pref_connection.cursor()
        try:
            self.__pref_connection.execute("""CREATE TABLE settings (
                user text,
                groceries real, 
                rent real,
                leisure real,
                insurance real, 
                energy real,
                transportation real)""")
            self.__cursor2.execute("INSERT INTO settings VALUES (:user, :groceries, :rent, :leisure, :insurance, :energy, :transportation)",
            {
                'user':username,
                'groceries':500,
                'rent':500,
                'leisure':500,
                'insurance':500,
                'energy':500,
                'transportation':500
            }) 
            self.__pref_connection.commit()
        except sqlite3.OperationalError:
            print("Database Wallet found. Creating Connection.")

    def change_settings(self, data):
        self.__cursor2.execute("UPDATE settings SET groceries = ?, rent = ?, leisure = ?, insurance = ?, energy = ?, transportation = ?  WHERE user = ?",
        (
            data[1],
            data[2],
            data[3],
            data[4],
            data[5],
            data[6],
            data[0]
        ))
        self.__pref_connection.commit()

    def add_transaction(self, transaction_data):
        self.__cursor.execute("INSERT INTO wallets VALUES (:username, :transaction_type, :date, :title_entry, :sender_entry, :address_entry, :money_entry, :category)",
        {
            'username':transaction_data[0],
            'transaction_type':transaction_data[1],
            'date':transaction_data[2],
            'title_entry':transaction_data[3],
            'sender_entry':transaction_data[4],
            'address_entry':transaction_data[5],
            'money_entry':transaction_data[6],
            'category':transaction_data[7]
        }) 
        self.commit_changes()
        self.read_database(transaction_data[0])

    def read_database(self, user):
        self.__cursor.execute(f"SELECT * FROM wallets")
        return self.__cursor.fetchall()
    
    def read_preferences(self):
        self.__cursor2.execute(f"SELECT * FROM settings")
        return self.__cursor2.fetchall()

    def commit_changes(self):
        self.__connection.commit()

    def close_connection(self):
        self.__connection.close()