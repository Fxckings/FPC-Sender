from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import threading
import time
import logging
import random

if TYPE_CHECKING:
    from cardinal import Cardinal

from .config import SpammerConfig
from ..utils.message_generator import MessageGenerator

logger = logging.getLogger("FPC.ChatSpammer.Scheduler")


class SpamScheduler:
    def __init__(self, cardinal: Cardinal, config: SpammerConfig):
        self._cardinal = cardinal
        self._config = config
        self._message_generator = MessageGenerator(config)
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False

    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        if self._running:
            logger.warning("Scheduler already running")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_spam_loop, daemon=True)
        self._thread.start()
        self._running = True
        logger.info(f"Spam scheduler started with {self._config.startup_delay}s delay")

    def stop(self) -> None:
        if not self._running:
            return

        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        self._running = False
        logger.info("Spam scheduler stopped")

    def _run_spam_loop(self) -> None:
        try:
            time.sleep(self._config.startup_delay)
            logger.info("Spam loop started")

            while not self._stop_event.is_set():
                self._send_spam_round()
                
                if self._stop_event.wait(timeout=self._config.interval_seconds):
                    break

        except Exception as e:
            logger.error(f"Error in spam loop: {e}", exc_info=True)
            self._notify_error(e)
        finally:
            self._running = False

    def _send_spam_round(self) -> None:
        if not self._config.chat_ids:
            logger.warning("No chat IDs configured")
            return

        message = self._message_generator.generate()
        success_count = 0
        fail_count = 0

        for chat_id in self._config.chat_ids:
            try:
                self._cardinal.send_message(chat_id=chat_id, message_text=message)
                success_count += 1
                logger.debug(f"Message sent to chat {chat_id}")
                
                time.sleep(random.uniform(0.5, 2.0))
                
            except Exception as e:
                fail_count += 1
                logger.error(f"Failed to send message to chat {chat_id}: {e}")

        logger.info(f"Spam round completed: {success_count} sent, {fail_count} failed")

    def _notify_error(self, error: Exception) -> None:
        if not self._config.notify_on_error:
            return

        try:
            if self._cardinal.telegram and self._cardinal.telegram.authorized_users:
                admin_id = self._cardinal.telegram.authorized_users[0]
                error_msg = f"⚠️ Ошибка в спамере:\n{str(error)}"
                self._cardinal.telegram.bot.send_message(admin_id, error_msg)
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")