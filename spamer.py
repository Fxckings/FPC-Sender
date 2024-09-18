from typing import TYPE_CHECKING
from cardinal import Cardinal

if TYPE_CHECKING:
    from cardinal import Cardinal

from FunPayAPI.updater.events import *
from FunPayAPI.common.enums import *
import logging
from locales.localizer import Localizer
import threading
from faker import Faker

logger = logging.getLogger("FPC.SpamerPlugin")
localizer = Localizer()
_ = localizer.translate

LOGGER_PREFIX = "Spamer-Plugin"
logger.info(f"{LOGGER_PREFIX} Активен")

NAME = "SpamerPlug-in"
VERSION = "0.0.1"
DESCRIPTION = """
Авто-отправляет мессаджы в чатики
"""
CREDITS = "@cloudecode"
UUID = "b15ccbb6-30a1-4524-b0fe-cc23cc5771ae"
SETTINGS_PAGE = False

SEND_EVERY = 1000 # время между отправками в секундах
START_TIMER = 15 #время на инициализацию кардинала

def init(cardinal: Cardinal):
    tg = cardinal.telegram
    bot = tg.bot

    logger.info(f"{LOGGER_PREFIX} Запускаю спам в чаты")
    threading.Timer(START_TIMER, spam4chats, args=[cardinal, bot]).start()

def spam4chats(c: Cardinal, bot):
    try:
        while True:
            chat_ids = ['flood', 'game-41', 'game-2', 'game-3', 'game-4', 'game-5', 'game-123']
            msg = Faker().sentence(nb_words=12)

            for chat_id in chat_ids:
                c.send_message(chat_id=chat_id, message_text=msg)
            
            time.sleep(SEND_EVERY)

    except Exception as e:
        logger.error(e)
        bot.send_message(c.telegram.authorized_users[0], 
                         f"Не смог отправить сообщение в чат 'flood'. Еррор: {e}")

def msg4eck(cardinal: Cardinal, msgev: NewMessageEvent):
    pass

BIND_TO_PRE_INIT = [init]
BIND_TO_NEW_MESSAGE = [msg4eck]
BIND_TO_DELETE = None
