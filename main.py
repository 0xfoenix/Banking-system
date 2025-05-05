import streamlit as st
from datetime import datetime
import pandas as pd
import json
import uuid
import time
import hashlib

user_file = "users.json"
pin_file = "utils.json"

'''
Helper functions to load and write to JSON and hash pin
'''
def read_json(file):
    if file == "utils.json":
        try:
            with open("utils.json", "r") as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            data = {"users":{

            },
            "next_account_number": 1}

            with open("utils.json", "w") as f:
                json.dump(data, f, indent=4, sort_keys = True)
                return data
    elif file == "users.json":
        try:
            with open("users.json", "r") as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            data = {"users":{

            },
            "next_account_number": 1}

            with open("users.json", "w") as f:
                json.dump(data, f, indent=4, sort_keys = True)
                return data
    else:
        return "File not found"


def write_json(data, filename):
    if filename == "utils.json":
        with open("utils.json", "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)
    elif filename == "users.json":
        with open("users.json", "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)
    else:
        return "File not found"
        

def hash_pin(pin):
    b_pin = f"{pin}".encode()
    sha256 = hashlib.sha256()
    sha256.update(b_pin)
    pin_hash = sha256.hexdigest()
    return pin_hash

'''
Initializing Classes
'''
# Create Transaction class
class Transaction():
    def __init__ (self, transaction_id, timestamp, transaction_type, amount,
                  source_account,  ending_balance, destination_account=None):
        
        self.transaction_id = transaction_id
        self.timestamp = timestamp
        self.transaction_type = transaction_type
        self.amount = amount
        self.source_account = source_account
        self.ending_balance = ending_balance
        if transaction_type == "Transfer":
            self.destination_account = destination_account   
        
    # Generate receipt
    def generate_receipt(self):
        '''
        generate receipts: Generates a receipt for every successful transfer

        returns a dictionary of transaction details
        '''


        if self.transaction_type == "Transfer":
            receipt = {
                "Transaction Id": self.transaction_id,
                "Time Stamp": self.timestamp,
                "Transaction Type": self.transaction_type,
                "Amount": self.amount,
                "Sender": self.source_account,
                "Receiver": self.destination_account
            }
            return receipt
    
    # Save transaction
    def save_to_history(self, account, transaction):
        '''
        save to history: Saves transaction to the necessary account's transaction history

        Args:

            account(Account): Account Instance where transaction will be stored

            transaction(Transaction): Transaction list to be stored

            return formatted string
        '''

        account.transaction_history.append(transaction)
        return "Transaction saved successfully"
        
            
        
# Create Bank Account
class Account():
    def __init__(self, account_name, account_number, balance, 
                  contact_info, creation_date, transaction_history=None):
        self.account_name = account_name
        self.account_number = account_number
        self.balance = balance
        self.contact_info = contact_info
        self.creation_date = creation_date
        self.transaction_history = transaction_history if transaction_history is not None else []
    
    def deposit(self, amount):
        '''
        deposit: Function to add money into your account without Transfer

        Args:
            amount(float): Amount to deposit

        returns formatted string detailing amount deposited
        '''

        user_data = read_json(user_file)
        acc_no = str(self.account_number)

        if amount:
            new_balance = self.balance + amount
            self.balance = new_balance
            transaction_id = str(uuid.uuid4()) + str(int(time.time()) * 1000)
            timestamp = datetime.now()
            transaction = Transaction(
                transaction_id,
                timestamp,
                "Deposit",
                amount,
                self.account_number,
                ending_balance = new_balance
            )

            user_data["users"][acc_no]["Balance"] = new_balance
            write_json(user_data, user_file)

            self.transaction_history.append(transaction)
            return f"Your deposit of {amount} is successful"

    # Withdraw
    def withdraw(self, amount):
        '''
        withdraw: Function to remove money into your account without Transfer

        Args:
            amount(float): Amount to withdraw

        returns formatted string detailing amount withdrawn
        '''
        user_data = read_json(user_file)
        acc_no = str(self.account_number)

        if amount < self.balance:
            new_balance = self.balance - amount
            self.balance = new_balance

            transaction_id = str(uuid.uuid4()) + str(int(time.time()) * 1000)
            timestamp = datetime.now()

            transaction = Transaction(
                transaction_id,
                timestamp,
                "Withdraw",
                amount,
                self.account_number,
                ending_balance = new_balance
            )

            user_data["users"][acc_no]["Balance"] = new_balance
            write_json(user_data, user_file)

            self.transaction_history.append(transaction)
            return f"Your withdrawal of {amount} is successful"
        
        else:
            return "Insufficient balance."

    # Check balance      
    def check_balance(self):
        '''
        check balance: Checks account balance

        returns formatted text detailing account_balance
        '''
        if self.account_number:
            return f"You have ${self.balance} in your account"
        else:
            return f"Please login"
    
    # Change pin
    def change_pin(self, old_pin, new_pin):
        '''
        change_pin: Function to change pin

        To avoid removal of the zeros before the non-zero digit that is common in int type, I had to use text_type for pin

        Args:
            old_pin(text): Your current pin

            new pin(text): The new pin you'll be using from now

        returns string
        '''

        account = str(self.account_number)
        pin_data = read_json(pin_file)
        for account in pin_data["users"].keys():
            if int(account) == self.account_number:
                if old_pin == pin_data["users"][account]["pin"]:
                    if new_pin == old_pin:
                        return f"Same pin as previous"
                    else:            
                        try:   
                            if account:         
                                pin_data["users"][account]["pin"] = new_pin
                                write_json(pin_data, pin_file)
                                return "Pin changed successfully"
                            else:
                                return "Account not found. Please create an account"
                        except Exception as e:
                            return f"Error accessing key {e}"
                else:
                    return "Old pin incorrect. Try again"
        
    def update_contact_info(self,new_info):
        '''
        update_contact_info: Function to update contact info

        Args:
            new_info(dict): Dictionary containing updated info for account owner

        returns formatted string
        '''
        user_data = read_json(user_file)
        account = str(self.account_number)

        if new_info:
            self.contact_info = new_info
            user_data["users"][account]["contact info"] = new_info
            write_json(user_data, user_file)
            return f"Contact info updated successfully"
        
    def get_transaction_history(self):
        '''
        get transaction history: Gets the transaction history of given account

        returns a list of transactions
        '''

        if self.transaction_history:
            return self.transaction_history
        else:
            return "No transactions yet"


# Creating the Bank
class Bank():
    def __init__(self, name):
        self.name = name
        self.accounts = []

    # Create Account
    def create_account(self, owner_name, initial_deposit, pin, contact_info):
        '''
        Create Account: Function to create account

        Args:

            Owner_name(str): Name of account owner

            Initial_deposit(float): Non zero Amount initially deposited into the account

            pin: 4 digits used to login to your account

            contact_info(dict): Contains other information about Account owner

        returns formatted string with account_number
        '''
 
        pin_data = read_json(pin_file)

        user_data = read_json(user_file)

        
        if owner_name and initial_deposit and pin and contact_info:
            
            creation_time = datetime.now()
            time_data = creation_time.strftime("%Y-%m-%d %H:%M:%S")
            transaction_history = []
            account_number = int(user_data["next_account_number"])
            acc_no = str(account_number)
           
            pin_data["users"].update({acc_no:{               
                "pin": pin,
                "attempts": 0
            }})

            write_json(pin_data, pin_file)

            accounts = Account(
                owner_name,
                account_number,
                initial_deposit,
                contact_info,
                creation_time,
                transaction_history
                )
            
            account_data = {
                "Account Name": owner_name,
                "Account Number": acc_no,
                "Balance": initial_deposit,
                "Other info": contact_info,
                "Created on": time_data,
                "Transaction History": transaction_history
            }

            user_data["users"].update({
                acc_no: account_data
            })


            self.accounts.append(accounts)
            user_data["next_account_number"] = account_number + 1

            write_json(user_data, user_file)

            return f"Account with account number {account_number:08d} successfully created."

    # Find account
    def find_account(self, account_number):
        '''
    Find account: Function to create account

    Args:

        account_number: account number to search for

    returns the matched Account instance otherwise None

    '''
        user_data = read_json(user_file)

        acc_no = str(account_number)

        acc_data = list(user_data["users"][acc_no].values())
        
        acc = Account(*acc_data)
        self.accounts.append(acc)

        for account in self.accounts:
            if acc_no == account.account_number:
                return account
                
        return None
        
    if "max_trials" not in st.session_state:
        st.session_state.max_trials = 3
    
    # Authentication
    def authenticate(self, account_number, pin):
        '''
        Authenticate: Function to verify pin and account number before login

        Args:
            account_number: The account that wants to login

            pin: Pin used to login

        
        returns formatted text
        '''

        pin_data = read_json(pin_file)
        acc_no = str(account_number)
        saved_pin = pin_data["users"][acc_no]["pin"]
        trials = pin_data["users"][acc_no]["attempts"]

        if trials >= (st.session_state.max_trials - 1):
            return "You have exceeded your login attempts. Please reach out to customer care"
        
        for acc_no in pin_data["users"].keys():
            if account_number == int(acc_no): 
                if pin == saved_pin:
                    pin_data["users"][acc_no]["attempts"] = 0

                    write_json(pin_data, pin_file)
                    return "Login successful"
                else:
                    pin_data["users"][acc_no]["attempts"] = int(pin_data["users"][acc_no]["attempts"]) + 1
                    remaining = (st.session_state.max_trials - trials)
                    write_json(pin_data, pin_file)
                    return f"Wrong Pin. You have {remaining} chances left"
        return "No account number found. Check the account number or Create an account"
        
            
            
    # Transfer function
    def transfer(self, from_account, to_account, amount):
        '''
        transfer: To transfer from one account(from_account) to another(to_account)

        Args:
            from_account: Account initiating the transfer

            to_account: Account receiving the transfer

            amount: Amount to be transferred

        
        returns formatted string detailing amount transferred
        '''
        user_data = read_json(user_file)
        f_acc = str(from_account)
        t_acc = str(to_account)

        source_account = self.find_account(from_account)
        
        destination_account = self.find_account(to_account)
        
        if source_account and destination_account:
            if source_account.balance >= amount:
                if amount > 0:
                    s_balance = (source_account.balance - amount)
                    d_balance = (destination_account.balance + amount)

                    transaction_id = str(uuid.uuid4()) + str(int(time.time()) * 1000)
                    timestamp = datetime.now()
                    transaction_sender = (
                        transaction_id,
                        timestamp,
                        "Transfer",
                        amount,
                        from_account,
                        s_balance,
                        to_account
                        )
                    
                    transaction_receiver = (
                        transaction_id,
                        timestamp,
                        "Transfer",
                        amount,
                        from_account,
                        d_balance,
                        to_account
                    )
                    tx_receipt = Transaction(transaction_sender)

                    source_account.balance = s_balance
                    destination_account.balance = d_balance


                    transaction_sender.save_to_history(source_account, transaction_sender)
                    transaction_receiver.save_to_history(destination_account, transaction_receiver)

                    user_data["users"][f_acc]["Transaction History"].append(transaction_sender)
                    user_data["users"][t_acc]["Transaction History"].append(transaction_receiver)
                    write_json(user_data, user_file)

                    result = tx_receipt.generate_receipt()

                    return result, f"Transfer successful"
            
                else:
                    return "Invalid amount"
            else:
                return "Insufficient amount. Please deposit"
        else:
            return "Accounts not found"

    # Save data      
    def save_data(self, filename):
        '''
        save_data: Saves account information to file, (specifically csv)

        Args:

            filename: The name of the csv file where the file will be saved


        returns formatted string detailing filename
        '''

        if not self.accounts:
            return []
        
        if filename:
            account_data = []
            for account in self.accounts:
                account_data.append({
                    "Name": account.account_name,
                    "Acc_no": account.account_number,
                    "Owner's Name": account.owner_name,
                    "Account Balance": account.balance,
                    "Other Info": account.contact_info,
                    "Created On": account.creation_date,
                    "Transaction History": account.transaction_history
                })

            account_df = pd.DataFrame(account_data)

            try:
                account_df.to_csv(f"{filename}.csv", index=False)
                return f"Saved to {filename}.csv successfully"
            except Exception as e:
                return f"Error saving file {e}"
        else:
            return "Please input a filename"
        
    # Load data
    def load_data(self, filename):
        '''
        load_data: Load data from file specifically csv

        Args:
            filename: The name of the file from which the data is loaded from

        
        returns formatted string detailing filename
        '''


        if not filename:
            return "Please input a valid filename"
        
        try:
            account_df = pd.read_csv(f"{filename}.csv")
            self.accounts = []

            for _, row in account_df.iterrows():
                account = Account(row['Name'], row['Acc_no'], row['Owner\'s Name'],
                                  row['Account Balance'],  row['Other Info'],
                                  row['Created On'], row['Transaction History'])
                
                self.accounts.append(account)
                return f"Loaded from {filename}.csv successfully"

        except ValueError as e:
            return f"Skipping Invalid Account: {e}"




