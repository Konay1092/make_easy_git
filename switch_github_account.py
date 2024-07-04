import json
import subprocess
import os
import signal
import sys

def get_current_git_user():
    """Get the current global Git user.name and user.email"""
    try:
        current_name = subprocess.check_output(
            ['git', 'config', '--global', 'user.name']
        ).strip().decode('utf-8')
        current_email = subprocess.check_output(
            ['git', 'config', '--global', 'user.email']
        ).strip().decode('utf-8')
        return current_name, current_email
    except subprocess.CalledProcessError:
        return None, None

def generate_ssh_key():
    """Generate or overwrite an SSH key and display the public key."""
    ssh_dir = os.path.expanduser('~/.ssh')
    key_path = os.path.join(ssh_dir, 'id_rsa')
    pub_key_path = os.path.join(ssh_dir, 'id_rsa.pub')
    
    os.makedirs(ssh_dir, exist_ok=True)
    subprocess.run(['ssh-keygen', '-t', 'rsa', '-b', '4096','-f', key_path, '-N', ''])

    print(f"SSH key generated and overwritten.")

    # Display only the SSH key part
    with open(pub_key_path, 'r') as pub_key_file:
        pub_key = pub_key_file.read().strip()
        if pub_key.startswith('ssh-rsa'):
            print("Your SSH key is:")
            print(pub_key)
        else:
            print("Generated key does not start with 'ssh-rsa'.")
            print(f"Full Key: {pub_key}")

def display_accounts(accounts, current_name, current_email):
    """Display the list of GitHub accounts."""
    print("-> Your GitHub Accounts:")
    print(f"| {'Index':<5} | {'Username':<20} | {'Email':<50} | {'Active':<7} |")
    print("="*94)
    for idx, account in enumerate(accounts, start=1):
        is_active = account['username'] == current_name and account['email'] == current_email
        active_sign = "*" if is_active else ""
        
        # Formatting strings with ANSI escape codes
        idx_colored = f"\033[92m{idx:<5}\033[0m" if is_active else f"{idx:<5}"
        username_colored = f"\033[92m{account['username']:<20}\033[0m" if is_active else f"{account['username']:<20}"
        email_colored = f"\033[92m{account['email']:<50}\033[0m" if is_active else f"{account['email']:<50}"
        active_colored = f"\033[92m{active_sign:<7}\033[0m" if is_active else f"{active_sign:<7}"
        
        print(f"| {idx_colored} | {username_colored} | {email_colored} | {active_colored} |")

    print()

def signal_handler(sig, frame):
    print("\nExiting program.")
    sys.exit(0)

def main_menu():
    while True:
        display_accounts(accounts, current_name, current_email)
        print("a    Add new account")
        print("c    Change account")
        print("u    Update an account")
        print("d    Delete an account")
        print("g    Generate SSH KEY")
        print("0    Exit")
        print()

        # User input to select an option
        choice = input("-> Choose an option: ").strip().lower()

        if choice == "0":
            print("Exiting.")
            break
        elif choice == "c":
            change_account()
        elif choice == "u":
            update_account()
        elif choice == "d":
            delete_account()
        elif choice == "a":
            add_account()
        elif choice == "g":
            generate_ssh_key()
        else:
            print("Invalid choice.")

def change_account():
    while True:
        print()
        print(f"{'-'*30}  'Change Account Section' {'-'*30}  ")
        display_accounts(accounts, current_name, current_email)
        print(" 0       -> Back Menu")
        print(" ctrl+c  -> Exist Program")
        try:
            change_index = input("Enter the index of the account to change to (0 to return to main menu): ").strip()
            if change_index == "0":
                return  # Return to main menu
            change_index = int(change_index) - 1
            if 0 <= change_index < len(accounts):
                selected_account = accounts[change_index]
                username = selected_account['username']
                email = selected_account['email']
                
                # Set global Git config
                subprocess.run(['git', 'config', '--global', 'user.name', username])
                subprocess.run(['git', 'config', '--global', 'user.email', email])
                print(f"Switched to account: {username} ({email})")
                
                # Prompt to generate SSH key
                generate_ssh = input("Do you want to generate an SSH key for this account? (y/n): ").lower()
                if generate_ssh in ['y', 'yes']:
                    generate_ssh_key()
            else:
                print("Invalid index.")
        except ValueError:
            print("Invalid input.")

def update_account():
    while True:
        print()
        print(f"{'-'*30}  'Update Account Section' {'-'*30}  ")
        display_accounts(accounts, current_name, current_email)
        print(" 0       -> Back Menu")
        print(" ctrl+c  -> Exist Program")
            
             # Return to main menu
        try:
            update_index= input("Enter the index of the account to update to (0 to return to main menu): ").strip()
            if update_index == "0":
                return  # Return to main menu
            update_index = int(update_index) - 1
            # update_index = int(input("Enter the index of the account to update: ")) - 1
            if 0 <= update_index < len(accounts):
                new_username = input("Enter new GitHub username: ")
                new_email = input("Enter new GitHub email: ")
                accounts[update_index]['username'] = new_username
                accounts[update_index]['email'] = new_email
                with open(accounts_file_path, 'w') as file:
                    json.dump({"accounts": accounts}, file)
                print("Account updated successfully.")
                break
            else:
                print("Invalid index.")
        except ValueError:
            print("Invalid input.")
    return_to_main_menu()

def delete_account():
    while True:
        print()
        print(f"{'-'*30}  'Delete Account Section' {'-'*30}  ")
        display_accounts(accounts, current_name, current_email)
        print(" 0       -> Back Menu")
        print(" ctrl+c  -> Exist Program")


        try:
            delete_index= input("Enter the index or number  of the account to delete : ").strip()
            if delete_index == "0":
                return  # Return to main menu
            delete_index = int(delete_index) - 1
            # delete_index = int(input("Enter the index of the account to delete: ")) - 1
            if 0 <= delete_index < len(accounts):
                accounts.pop(delete_index)
                with open(accounts_file_path, 'w') as file:
                    json.dump({"accounts": accounts}, file)
                print("Account deleted successfully.")
                break
            else:
                print("Invalid index.")
        except ValueError:
            print("Invalid input.")
    return_to_main_menu()

def add_account():
    print()
    print(f"{'-'*30}  'Add Account Section' {'-'*30}  ")
    new_username = input("Enter new GitHub username: ")
    new_email = input("Enter new GitHub email: ")
    accounts.append({"username": new_username, "email": new_email})
    with open(accounts_file_path, 'w') as file:
        json.dump({"accounts": accounts}, file)
    print("New account added successfully.")
    return_to_main_menu()

def return_to_main_menu():
    input("Press Enter to return to the main menu...")

# Register the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

# Load or create accounts from JSON file
accounts_file_path = os.path.expanduser('~/github_change_accounts/accounts.json')
if not os.path.exists(accounts_file_path):
    os.makedirs(os.path.dirname(accounts_file_path), exist_ok=True)
    with open(accounts_file_path, 'w') as file:
        json.dump({"accounts": []}, file)

# Try to read the accounts file
try:
    with open(accounts_file_path, 'r') as file:
        data = json.load(file)
except json.JSONDecodeError:
    data = {"accounts": []}
    with open(accounts_file_path, 'w') as file:
        json.dump(data, file)

accounts = data.get('accounts', [])

# Check if accounts are empty and populate with current global Git config
current_name, current_email = get_current_git_user()
if not accounts and current_name and current_email:
    accounts.append({"username": current_name, "email": current_email})
    with open(accounts_file_path, 'w') as file:
        json.dump({"accounts": accounts}, file)

# Run the main menu
main_menu()
