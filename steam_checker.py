import requests
import time
from datetime import datetime
from colorama import init, Fore
import json

init(autoreset=True)

LIST_FILE = "list.txt"
FETCHED_FILE = "fetched.txt"
VALID_FILE = "valid.txt"
STEAM_URL = "https://steamcommunity.com/id/"
CHECK_DELAY = 2
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1338956655378829385/nlv39EX77AzoYZ9yIuhWT7cGkA8UpH97KqhV06_aRou3kc11XxbXdO-D8liFG4g61AzH"  # webhook ekle kanzi oraya atıyor logu

def send_discord_log(message):
    payload = {
        "content": message
    }
    try:
        requests.post(DISCORD_WEBHOOK, data=json.dumps(payload), headers={"Content-Type": "application/json"})
    except requests.RequestException:
        print("Failed to send Discord log.")

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colors = {"INFO": Fore.BLUE, "SUCCESS": Fore.GREEN, "ERROR": Fore.RED}
    color = colors.get(level, Fore.WHITE)
    log_message = f"[{timestamp}] [{level}] {message}"
    print(f"{color}{log_message}")

def read_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        return set()

def write_file(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(data))

def check_username(username):
    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(STEAM_URL + username, timeout=15)
            if "The specified profile could not be found." in response.text:
                log(f"{username} is available and unused!", "ERROR")
                send_discord_log(f"{username} Kullanıcı Adı Boşta! @everyone")
                return False
            return True
        except requests.RequestException:
            log(f"Request failed for {username}, retrying {attempt + 1}/{retries}...", "ERROR")
            time.sleep(5)
    return False

def main():
    usernames = read_file(LIST_FILE)
    fetched = read_file(FETCHED_FILE)
    valid = read_file(VALID_FILE)
    
    to_fetch = usernames - fetched
    log(f"Checking {len(to_fetch)} usernames...")
    
    for username in to_fetch:
        log(f"Checking {username}...")
        if check_username(username):
            valid.add(username)
        fetched.add(username)
        time.sleep(CHECK_DELAY)
    
    write_file(VALID_FILE, valid)
    write_file(FETCHED_FILE, fetched)
    log("Process completed.", "SUCCESS")

if __name__ == "__main__":
    main()
