import streamlit as st
from datetime import datetime
import pandas as pd
import uuid
import time

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
        account.transaction_history.append(transaction)
        
            
        
# Create Bank Account
class Account():
    def __init__(self, account_name, account_number, balance, 
                 pin, contact_info, creation_date, transaction_history=None):
        self.account_name = account_name
        self.account_number = account_number
        self.balance = balance
        self.pin = pin
        self.contact_info = contact_info
        self.creation_date = creation_date
        self.transaction_history = transaction_history if transaction_history is not None else []
    
    def deposit(self, account, amount):
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
                account,
                ending_balance = new_balance
            )
            self.transaction_history.append(transaction)
            return f"Your deposit of {amount} is successful"

    # Witdraw
    def withdraw(self, account, amount):
        if amount <= (self.balance - 1000):
            new_balance = self.balance - amount
            self.balance = new_balance
            transaction_id = str(uuid.uuid4()) + str(int(time.time()) * 1000)
            timestamp = datetime.now()
            transaction = Transaction(
                transaction_id,
                timestamp,
                "Withdraw",
                amount,
                account,
                ending_balance = new_balance
            )
            self.transaction_history.append(transaction)
            return f"Your withdrawal of {amount} is successful"
        else:
            return "Insufficient balance."

    # Check balance      
    def check_balance(self):
            return f"You have ${self.balance} in your account"
    
    # Change pin
    def change_pin(self, old_pin, new_pin):
        if new_pin == old_pin:
            return f"Same pin as previous"
        else:
            self.pin = new_pin
            return "Pin changed successfully"
        
    def update_contact_info(self,new_info):
        if new_info:
            self.contact_info = new_info
            return f"Contact info updated successfully"
        
    def get_transaction_history(self):
        if self.transaction_history:
            return self.transaction_history
        else:
            return "No transactions yet"


# Creating the Bank
class Bank():
    def __init__(self, name):
        self.name = name
        self.accounts = []
        self.next_account_number = 1
        if self.accounts and len(self.accounts) > 0:
            self.next_account_number = max([a.account_number for a in self.accounts]) + 1

    # Create Account
    def create_account(self, owner_name, initial_deposit, pin, contact_info):
        if owner_name and initial_deposit and pin and contact_info:
            creation_time = datetime.now()
            transaction_history = []
            
            accounts = Account(
                owner_name,
                self.next_account_number,
                initial_deposit,
                pin,
                contact_info,
                creation_time,
                transaction_history
                )

            self.accounts.append(accounts)
            self.next_account_number += 1

            return f"Account with account number -{self.next_account_number} successfully created"

    # Find account
    def find_account(self, account_number):
        for account in self.accounts:
            if account_number == account.account_number:
                return account
        return None
    
    # Authentication
    def authenticate(self, account_number, pin):
        if "trial" not in st.session_state:
            st.session_state.trial = 0
            st.session_state.max_trials = 3
        
        if st.session_state.trial >= st.session_state.max_trials:
            return "You have exceeded your login attempts. Please reach out to customer care"
        
        for account in self.accounts:
            if account_number == account.account_number and pin == account.pin:
                st.session_state.trial = 0
                return "Login successful"
                
        st.session_state.trial += 1
        remaining = st.session_state.max_trials - st.session_state.trial
        return f"Wrong Pin. You have {remaining} left"
            
            
    # Transfer function
    def transfer(self, from_account, to_account, amount):
        source_account = self.find_account(from_account)
        destination_account = self.find_account(to_account)

        s_balance = source_account.balance - amount
        d_balance = destination_account.balance + amount
        if source_account and destination_account:
            if (source_account.balance + 10) >= amount:
                if amount > 0:
                    transaction_id = str(uuid.uuid4()) + str(int(time.time()) * 1000)
                    timestamp = datetime.now()
                    transaction_sender = Transaction(
                        transaction_id,
                        timestamp,
                        "Transfer",
                        amount,
                        from_account,
                        s_balance,
                        to_account
                        )
                    
                    transaction_receiver = Transaction(
                        transaction_id,
                        timestamp,
                        "Transfer",
                        amount,
                        from_account,
                        d_balance,
                        to_account
                    )

                    transaction_sender.generate_receipt()
                    transaction_sender.save_to_history(source_account, transaction_sender)
                    transaction_receiver.save_to_history(destination_account, transaction_receiver)
            
                else:
                    return "Invalid amount"
            else:
                return "Insufficient amount. Please deposit"
        else:
            return "Accounts not found"

    # Save data      
    def save_data(self, filename):
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
                    "Account Pin": account.pin,
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
        if not filename:
            return "Please input a valid filename"
        
        try:
            account_df = pd.read_csv(f"{filename}.csv")
            account_data = []

            for _, row in account_df.iterrows():
                account = Account(row['Name'], row['Acc_no'], row['Owner\'s Name'],
                                  row['Account Balance'], row['Account Pin'], row['Other Info'],
                                  row['Created On'], row['Transaction History'])
                
                self.accounts.append(account)
                return f"Loaded from {filename}.csv successfully"

        except ValueError as e:
            return f"Skipping Invalid Account: {e}"




