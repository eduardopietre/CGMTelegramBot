import requests
import time
from CGMTelegramBot.logger import LOGGER
from private import BOT_TOKEN, NIGHTSCOUT_URL, SECRET
from CGMTelegramBot import CGMBot


def get_username_whitelist(file: str = "username_whitelist.txt") -> set[str]:
    usernames = set()

    with open(file, "r") as file:
        for line in file:
            user = line.strip()
            if user:
                usernames.add(user)

    return usernames


def wait_internet_connection():
    def connected_to_internet(url='http://www.google.com/', timeout=5):
        try:
            _ = requests.head(url, timeout=timeout)
            return True
        except requests.ConnectionError:
            LOGGER.info("No internet connection available.")
        return False

    while not connected_to_internet:
        time.sleep(60)


if __name__ == '__main__':
    wait_internet_connection()

    username_whitelist = get_username_whitelist()

    bot = CGMBot(
        url=NIGHTSCOUT_URL,
        secret=SECRET,
        token=BOT_TOKEN,
        database_file="mgb_database.json",
        whitelisted_users=username_whitelist
    )

    bot.run()
