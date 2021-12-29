from telegram import Update
from telegram.ext import CallbackContext

from . import utils
from . import settings
from .timer import RepeatedTimer
from .database import Database
from .basebot import BaseBot



def commands_helper_str(only_mute=False):
    other_helps = [
        "/start  -  Refaz a autenticação do usuário.",
        "/g  -  Mostra a glicose atual.",
        "/glicose  -  Mostra a glicose atual.",
    ]

    mute_help = [
        "/silencia20  -  Silencia por 20 minutos.",
        "/silencia40  -  Silencia por 40 minutos.",
        "/silencia60  -  Silencia por 60 minutos.",
        "/silencia90  -  Silencia por 90 minutos.",
        "/remover_silenciar  -  Remove o silenciar.",
    ]

    if only_mute:
        helps = mute_help
    else:
        helps = other_helps + mute_help

    return "\n".join(helps)



class CGMBot(BaseBot):

    def __init__(self, token: str, database_file: str, whitelisted_users: set[str]):
        super().__init__(token, database_file, whitelisted_users)

        self.database = Database()
        self.repeating_check = None
        self.previous_measure = None


    def mute_for(self, update: Update, context: CallbackContext, minutes: int):
        username = update.effective_user.username
        if self.userDataManager.contains_username(username):
            self.userDataManager.silence_username_for_minutes(username, minutes)
            update.message.reply_text(
                f"Voltaremos a avisar em {minutes} minutos.\n{commands_helper_str(only_mute=True)}"
            )
        else:
            update.message.reply_text(
                f"Lamentamos, não foi possível silenciar.\n{commands_helper_str(only_mute=True)}"
            )


    def check_last_reading(self) -> None:
        latest_measure = self.database.latest_measure()

        if latest_measure != self.previous_measure:
            self.previous_measure = latest_measure

            if latest_measure.triggers_alert():
                # Message users
                report_message = latest_measure.message()
                message = f"{report_message}\n{commands_helper_str(only_mute=True)}"
                self.alert_all_users(message)


    def alert_all_users(self, message):
        for username, chat_id in self.auth_manager.items():
            if not self.userDataManager.is_username_silenced(username):
                self.send_message_to_chat_id(chat_id, message)


    # Start commands handlers


    def cmd_start(self, update: Update, context: CallbackContext) -> None:
        # Send a message when the command /start is issued.

        user = update.effective_user
        is_auth = self.auth_manager.is_user_authorized(user)
        message = utils.greetings_for_user(user, is_auth)

        if is_auth:
            self.authenticate_user(user, update.effective_message.chat_id)

        update.message.reply_markdown_v2(message)


    def cmd_text(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(
            f"Não há comandos com essas palavras.\n{commands_helper_str()}"
        )


    def cmd_glucose(self, update: Update, context: CallbackContext) -> None:
        if self.previous_measure:
            message = self.previous_measure.message()
            update.message.reply_text(message)
        else:
            update.message.reply_text(
                f"Lamentamos, mas não encontramos a última aferição.\n{commands_helper_str()}"
            )


    def wrapper_cmd_mute_for(self, time: int):
        def _mute(update: Update, context: CallbackContext):
            self.mute_for(update, context, time)

        return _mute


    def cmd_unmute(self, update: Update, context: CallbackContext) -> None:
        username = update.effective_user.username
        if self.userDataManager.is_username_silenced(username):
            self.userDataManager.unmute_username(username)
            update.message.reply_text(
                f"Silenciado removido.\n{commands_helper_str(only_mute=True)}"
            )
        else:
            update.message.reply_text(
                f"Você não aparenta estar silenciado.\n{commands_helper_str(only_mute=True)}"
            )


    # End command handlers


    def run(self) -> None:
        # Set it up to check every X seconds
        self.repeating_check = RepeatedTimer(settings.CHECK_DELAY, self.check_last_reading)

        handlers = [
            ("start", self.cmd_start),
            ("g", self.cmd_glucose),
            ("glicose", self.cmd_glucose),
            ("silencia20", self.wrapper_cmd_mute_for(20 - 1)),
            ("silencia40", self.wrapper_cmd_mute_for(40 - 1)),
            ("silencia60", self.wrapper_cmd_mute_for(60 - 1)),
            ("silencia90", self.wrapper_cmd_mute_for(90 - 1)),
            ("remover_silenciar", self.cmd_unmute)
        ]

        self.base_run(handlers, self.cmd_text)
