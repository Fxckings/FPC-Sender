from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import logging

if TYPE_CHECKING:
    from cardinal import Cardinal

from FunPayAPI.updater.events import NewMessageEvent

from plugins.chat_spammer.core.config import SpammerConfig
from plugins.chat_spammer.core.spam_scheduler import SpamScheduler
from plugins.chat_spammer.ui.telegram_handler import TelegramUIHandler
from plugins.chat_spammer.utils.constants import PluginMetadata

logger = logging.getLogger("FPC.ChatSpammer")

NAME = PluginMetadata.NAME
VERSION = PluginMetadata.VERSION
DESCRIPTION = PluginMetadata.DESCRIPTION
CREDITS = PluginMetadata.CREDITS
UUID = PluginMetadata.UUID
SETTINGS_PAGE = True


class ChatSpammerPlugin:
    def __init__(self, cardinal: Cardinal):
        self._cardinal = cardinal
        self._config = SpammerConfig.load()
        self._scheduler: Optional[SpamScheduler] = None
        self._telegram_handler: Optional[TelegramUIHandler] = None
        
        logger.info("ChatSpammer plugin initialized")

    def initialize_telegram(self) -> None:
        if self._cardinal.telegram:
            self._telegram_handler = TelegramUIHandler(
                bot=self._cardinal.telegram.bot,
                tg=self._cardinal.telegram,
                config=self._config,
                uuid=UUID,
                on_start=self.start_spamming,
                on_stop=self.stop_spamming
            )
            self._telegram_handler.register_handlers()
            logger.info("Telegram handlers registered")

    def start_spamming(self) -> None:
        if self._scheduler and self._scheduler.is_running():
            logger.warning("Spam scheduler already running")
            return

        self._scheduler = SpamScheduler(
            cardinal=self._cardinal,
            config=self._config
        )
        self._scheduler.start()
        logger.info("Spam scheduler started")

    def stop_spamming(self) -> None:
        if self._scheduler:
            self._scheduler.stop()
            self._scheduler = None
            logger.info("Spam scheduler stopped")

    def handle_message(self, event: NewMessageEvent) -> None:
        pass


_plugin_instance: Optional[ChatSpammerPlugin] = None


def init(cardinal: Cardinal) -> None:
    global _plugin_instance
    _plugin_instance = ChatSpammerPlugin(cardinal)
    _plugin_instance.initialize_telegram()
    
    if _plugin_instance._config.enabled:
        _plugin_instance.start_spamming()


def msg_hook(cardinal: Cardinal, event: NewMessageEvent) -> None:
    if _plugin_instance:
        _plugin_instance.handle_message(event)


BIND_TO_PRE_INIT = [init]
BIND_TO_NEW_MESSAGE = [msg_hook]
BIND_TO_DELETE = None