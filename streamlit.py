import streamlit as st
import pandas as pd
import json
from main import Bank, hash_pin, read_json

st.title("Welcome to the Royal Bank")
    
# Initialize bank
if 'bank' not in st.session_state:
    st.session_state.bank = Bank("The Royal Bank")
    
# Initialize login and account number
if 'login' not in st.session_state:
    st.session_state.login = False
    st.session_state.account_number = None

# Initialize trial
if 'trial' not in st.session_state:
    st.session_state.trial = 0

# Initialize max trials
if 'max_trials' not in st.session_state:
    st.session_state.max_trials = 3

if not st.session_state.login:
    st.sidebar.title("Home Page Functions")
    function_option = st.sidebar.selectbox("Home Page Functions", ["Create New Account",
                                               "Login", "About/Help Information"])
else:
    st.sidebar.title("Main Bank Functions")
    function_option = st.sidebar.selectbox("What do you want to do today?",
                                           ["Deposit", "Withdraw", "Transfer", "Check Balance",
                                            "View Transaction history", "Update account information",
                                            "Change PIN", "Logout"])

# Create New account  
if function_option == "Create New Account":
    st.header("Create New Account")

    with st.form("Create Account"):
        name =  st.text_input("Full name", placeholder="Please enter your full name")
        deposit =st.number_input("Initial Deposit", placeholder="Please input the amount you're ready to deposit", min_value=100)
        input_pin = st.text_input("Pin", placeholder="Please enter your pin", type="password", max_chars=4)
        phone = st.text_input("Phone_number", placeholder="Please input your number")
        address = st.text_input("Address", placeholder="Please input your address")
        next_of_kin = st.text_input("Next of Kin(Optional)", placeholder="Please add the name of your next of kin")
        next_of_kin_phone = st.text_input("Next of Kin phone(Optional)", placeholder="Please add the phone of your next of kin")

        contact_info = {
           "phone": phone,
            "address": address,
           "next of kin": next_of_kin, 
           "next of kin phone": next_of_kin_phone
       }

        if st.form_submit_button("Create Account"):
            if name and deposit and input_pin and contact_info:
               pin = hash_pin(input_pin)
               result = st.session_state.bank.create_account(name, deposit, pin, contact_info)
               st.success(result)
            else:
               st.error("Please input all necessary details")

# Login functions
elif function_option == "Login":
    st.header("Login Page")
        
    account_number = st.number_input("Account Number", placeholder="Please enter your account number", step=1)
    input_pin = st.text_input("pin", placeholder="Please input your pin", type="password", max_chars=4)
    
    trial = st.session_state.trial
    max_trials = st.session_state.max_trials
    user_file = "user_data"
    users_data = read_json(user_file)



    if st.button("Login"):
        if account_number and input_pin:
            if len(input_pin) == 4:
                for acc_no in users_data["users"].keys():
                    if trial <= (max_trials - 1):
                        if account_number == int(acc_no):
                            pin = hash_pin(input_pin)
                            result = st.session_state.bank.authenticate(account_number, pin)
                            st.success(result)

                            if result == "Login successful":
                                st.session_state.login = True
                                st.session_state.account_number = account_number
                            
                                st.rerun()
                        else:
                            st.info("Account not found. Please create an account or check input")
                    else:
                        st.warning("Please refer to Support ")
            else:
                st.info("Pin must be a minimum of 4 digits")
        else:
            st.info("Please input the necessary details to login")
            
    

                            
    
# Other info
elif function_option == "About/Help Information":
    st.header("Help")

    st.markdown("Welcome to the Royal Bank")
    st.markdown("The best bank for you today")
    st.markdown("We work towards the imporvement of our customers' financial lives")
    st.markdown("If you'd like to join us, please create an account or login")
    st.markdown("If you have more questions, please reach out to us on 0xfoenix@gmail.com")

# Initialize login
if st.session_state.login:
    for account in st.session_state.bank.accounts:
        if account.account_number == st.session_state.account_number:
            st.title(f"Welcome to the Royal Bank, {account.account_name}")

    
# Deposit function
if function_option == "Deposit":
    if st.session_state.account_number:
        amount = st.number_input("Amount", placeholder="Input the amount you want to deposit", min_value=100)
        
        for account in st.session_state.bank.accounts:
            if st.button("Deposit"):
                if account.account_number == st.session_state.account_number:
                    if amount:
                        if amount >= 100:
                            result = account.deposit(amount)
                            st.success(result)
                        else:
                            st.info("Please increase deposit amount")
                    else:
                        st.info("Please input a valid amount")
                else:
                    st.info("Account not found. Please create an account")
    else:
        st.info("Please log in")


# Withdraw function
elif function_option == "Withdraw":
    if st.session_state.account_number:
        amount = st.number_input("Amount", placeholder="Input the amount you wish to withdraw", min_value=10)

        for account in st.session_state.bank.accounts:
            if st.button("Withdraw"):
                if account.account_number == st.session_state.account_number:
                    if amount:
                        if amount >=10:
                            result = account.withdraw(amount)
                            st.success(result)
                        else:
                            st.info("Please increase amount to withdraw")
                    else:
                        st.info("Please input a valid amount")
                else:
                    st.warning("Account not found. Please create an account or login")
    else:
        st.warning("Please log in or Create an account")
    
# Transfer function
elif function_option == "Transfer":
    if st.session_state.account_number:
        d_account = st.number_input("Account", placeholder="Input the account you want to transfer to")
        amount = st.number_input("Amount", placeholder="Input the amount you want to transfer")
        s_account = st.session_state.account_number
            
        if st.button("Transfer"):
            if d_account and amount:
                for account in st.session_state.bank.accounts:
                    if d_account == account.account_number:
                        if amount > 0:
                            result = st.session_state.bank.transfer(s_account, d_account, amount)
                            st.success(result)
                        else:
                            st.info("Please enter a valid amount to withdraw")
                    else:
                        st.warning("Account doesn't exist. Please check the account number again")
            else:
                st.warning("Please input the necessary details")
    else:
        st.warning("Please login or create an account")

# Check balance function
elif function_option == "Check Balance":
    if st.session_state.account_number:
        if st.button("Check Balance"):
            for account in st.session_state.bank.accounts:
                if account.account_number == st.session_state.account_number:
                    result = account.check_balance()
                    st.success(result)
                else:
                    st.warning("Account not found. Please login or create an account")
        
    else:
        st.warning("Please login or create an account")

# View Transaction history
elif function_option == "View Transaction history":
    if st.session_state.account_number:
        if st.button("View tx history"):
            for account in st.session_state.bank.accounts:
                if account.account_number == st.session_state.account_number:
                    tx_data = account.get_transaction_history()

                    tx_df =  pd.DataFrame(tx_data)
                    st.dataframe(tx_df)
                else:
                    st.info("Account not found. Please login or create an account")
        else:
            st.info("Please login or create an account")
    
# Update an account info
elif function_option == "Update account information":
    if st.session_state.account_number:
        for account in st.session_state.bank.accounts:
            if account.account_number == st.session_state.account_number:

                with st.form("Edit contact info"):
                    edit_phone = st.text_input("Phone_number", placeholder="Please input your number", value=account.contact_info["phone"])
                    edit_address = st.text_input("Address", placeholder="Please input your address", value=account.contact_info["address"])
                    edit_next_of_kin = st.text_input("Next of Kin(Optional)", placeholder="Please add the name of your next of kin", value=account.contact_info["next of kin"])
                    edit_next_of_kin_phone = st.text_input("Next of Kin phone(Optional)", placeholder="Please add the phone of your next of kin", value=account.contact_info["next of kin phone"])

                    if st.form_submit_button("Edit Info"):
                        if edit_phone and edit_address and edit_next_of_kin and edit_next_of_kin_phone:
                            new_info = {
                                edit_phone,
                                edit_address,
                                edit_next_of_kin,
                                edit_next_of_kin_phone
                            }

                            result = account.update_contact_info(new_info)
                            st.success(result)
                        else:
                            st.info("Please input the necessary details")
            
            else:
                st.info("Account not found. Please create an account or login")
    else:
        st.info("Please create an account or login")

# Change PIN
elif function_option == "Change PIN":
    if st.session_state.account_number:
        i_new_pin = st.text_input("New Pin", placeholder="Please input your new pin", type="password", max_chars=4)
        i_new_pin2 = st.text_input("New Pin", placeholder="Please input your new pin", type="password", max_chars=4)
        i_old_pin = st.text_input("Old Pin", placeholder="Please input your current pin", type="password", max_chars=4)

        if st.button("Change PIN"):
            for account in st.session_state.bank.accounts:
                if st.session_state.account_number == account.account_number:
                        if i_old_pin and i_new_pin and i_new_pin2:
                            old_pin = hash_pin(i_old_pin)
                            new_pin = hash_pin(i_new_pin)
                            new_pin2 = hash_pin(i_new_pin2)
                            if new_pin == new_pin2:
                                result = account.change_pin(old_pin, new_pin)
                                st.success(result)
                            else:
                                st.info("Pin does not match")
                        else:
                            st.info("Please input pin")
                        
                else:
                    st.info("Account not found. Please create an account or log in")
    else:
        st.info("Please create a new account or login")

    
# Log out
elif function_option == "Logout":
    if st.session_state.account_number:
        if st.button("Logout"):
            st.session_state.login = False
            st.session_state.account_number = None
            st.rerun()
    else:
        st.info("Please login or create an account")
            
            
