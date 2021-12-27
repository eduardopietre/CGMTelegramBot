from private import BOT_TOKEN
from CGMTelegramBot import CGMBot


def get_username_whitelist(file: str = "username_whitelist.txt") -> set[str]:
    usernames = set()

    with open(file, "r") as file:
        for line in file:
            user = line.strip()
            if user:
                usernames.add(user)

    return usernames


if __name__ == '__main__':
    username_whitelist = get_username_whitelist()

    bot = CGMBot(
        token=BOT_TOKEN,
        database_file="mgb_database.json",
        whitelisted_users=username_whitelist
    )

    bot.run()
