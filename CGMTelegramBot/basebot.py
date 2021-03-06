from typing import Any

from telegram import User
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from .authentication import AuthManager
from .logger import LOGGER
from .userdata import UserDataManager



class BaseBot:

    def __init__(self, token: str, database_file: str, whitelisted_users: set[str]):
        LOGGER.info(f"BaseBot __init__")

        self.token = token
        self.auth_manager = AuthManager(database_file, whitelisted_users)
        self.userDataManager = UserDataManager()

        # Create the Updater and pass it your bot's token.
        self.updater = Updater(self.token)


    def authenticate_user(self, user: User, chat_id: int):
        LOGGER.info(f"BaseBot authenticate_user {user=} {chat_id=}")

        username = user.username

        if username is None:  # Security checks
            return

        self.auth_manager.set_user_chat_id(username, chat_id)
        self.userDataManager.init_username(username)


    def is_user_authenticate(self, user: User):
        LOGGER.info(f"BaseBot is_user_authenticate {user=}")

        self.auth_manager.is_user_authorized(user)


    def send_message_to_chat_id(self, chat_id: int, message: str) -> None:
        LOGGER.info(f"BaseBot send_message_to_chat_id {chat_id=} {message=}")

        self.updater.bot.send_message(chat_id, message)


    def send_message_to_username(self, username: str, message: str) -> None:
        LOGGER.info(f"BaseBot send_message_to_username {username=} {message=}")

        chat_id = self.auth_manager.chat_id_for_username(username)
        if chat_id:
            self.updater.bot.send_message(chat_id, message)
        else:
            LOGGER.warning(f"ChatId for username {username} not found.")


    def base_run(self, handlers: [(str, Any)], text_handler: Any) -> None:
        LOGGER.info(f"BaseBot base_run")

        # Register handlers
        dispatcher = self.updater.dispatcher

        for command, func_handler in handlers:
            dispatcher.add_handler(CommandHandler(command, func_handler))


        # on non command i.e message - echo the message on Telegram
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()
