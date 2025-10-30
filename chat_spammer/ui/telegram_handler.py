from __future__ import annotations
from typing import TYPE_CHECKING, Callable
import logging

if TYPE_CHECKING:
    from telebot import TeleBot
    from telebot.types import CallbackQuery, Message
    from tg_bot import TgBot

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..core.config import SpammerConfig
from ..utils.constants import UIConstants, CallbackData
from tg_bot import CBT

logger = logging.getLogger("FPC.ChatSpammer.TelegramUI")


class TelegramUIHandler:
    def __init__(
        self,
        bot: TeleBot,
        tg: TgBot,
        config: SpammerConfig,
        uuid: str,
        on_start: Callable,
        on_stop: Callable
    ):
        self._bot = bot
        self._tg = tg
        self._config = config
        self._uuid = uuid
        self._on_start = on_start
        self._on_stop = on_stop
        
        self._awaiting_interval: set[int] = set()
        self._awaiting_chat: set[int] = set()
        self._awaiting_message: set[int] = set()
        self._removal_chat_mode: set[int] = set()
        self._removal_message_mode: set[int] = set()

    def register_handlers(self) -> None:
        self._tg.cbq_handler(self._show_main_settings, lambda c: f"{CBT.PLUGIN_SETTINGS}:{self._uuid}" in c.data)
        self._tg.cbq_handler(self._toggle_enabled, lambda c: CallbackData.TOGGLE in c.data)
        self._tg.cbq_handler(self._start_spam, lambda c: CallbackData.START in c.data)
        self._tg.cbq_handler(self._stop_spam, lambda c: CallbackData.STOP in c.data)
        self._tg.cbq_handler(self._request_interval, lambda c: CallbackData.INTERVAL in c.data)
        self._tg.cbq_handler(self._show_chats, lambda c: CallbackData.CHATS_LIST in c.data)
        self._tg.cbq_handler(self._request_add_chat, lambda c: CallbackData.ADD_CHAT in c.data)
        self._tg.cbq_handler(self._request_remove_chat, lambda c: CallbackData.REMOVE_CHAT in c.data)
        self._tg.cbq_handler(self._show_messages, lambda c: CallbackData.MESSAGES_LIST in c.data)
        self._tg.cbq_handler(self._request_add_message, lambda c: CallbackData.ADD_MESSAGE in c.data)
        self._tg.cbq_handler(self._request_remove_message, lambda c: CallbackData.REMOVE_MESSAGE in c.data)
        self._tg.cbq_handler(self._toggle_faker, lambda c: CallbackData.TOGGLE_FAKER in c.data)
        self._tg.cbq_handler(self._toggle_random, lambda c: CallbackData.TOGGLE_RANDOM in c.data)
        
        self._tg.msg_handler(self._handle_interval_input, func=lambda m: m.from_user.id in self._awaiting_interval)
        self._tg.msg_handler(self._handle_chat_input, func=lambda m: m.from_user.id in self._awaiting_chat)
        self._tg.msg_handler(self._handle_message_input, func=lambda m: m.from_user.id in self._awaiting_message)
        self._tg.msg_handler(self._handle_chat_removal, func=lambda m: m.from_user.id in self._removal_chat_mode)
        self._tg.msg_handler(self._handle_message_removal, func=lambda m: m.from_user.id in self._removal_message_mode)

    def _show_main_settings(self, call: CallbackQuery) -> None:
        try:
            kb = InlineKeyboardMarkup(row_width=2)
            
            kb.add(
                InlineKeyboardButton(
                    "Включен:",
                    callback_data=CallbackData.TOGGLE
                ),
                InlineKeyboardButton(
                    UIConstants.CHECK_MARK if self._config.enabled else UIConstants.CROSS_MARK,
                    callback_data=CallbackData.TOGGLE
                )
            )
            
            kb.row(
                InlineKeyboardButton(
                    f"{UIConstants.PLAY} Запустить",
                    callback_data=CallbackData.START
                ),
                InlineKeyboardButton(
                    f"{UIConstants.STOP} Остановить",
                    callback_data=CallbackData.STOP
                )
            )
            
            kb.add(
                InlineKeyboardButton(
                    f"Интервал: {self._config.interval_seconds}с",
                    callback_data=CallbackData.INTERVAL
                )
            )
            
            kb.add(
                InlineKeyboardButton(
                    f"📋 Чаты ({len(self._config.chat_ids)})",
                    callback_data=CallbackData.CHATS_LIST
                )
            )
            
            kb.add(
                InlineKeyboardButton(
                    f"💬 Сообщения ({len(self._config.message_templates)})",
                    callback_data=CallbackData.MESSAGES_LIST
                )
            )
            
            kb.add(
                InlineKeyboardButton(
                    "Faker:",
                    callback_data=CallbackData.TOGGLE_FAKER
                ),
                InlineKeyboardButton(
                    UIConstants.CHECK_MARK if self._config.use_faker else UIConstants.CROSS_MARK,
                    callback_data=CallbackData.TOGGLE_FAKER
                )
            )
            
            kb.add(
                InlineKeyboardButton(
                    "Случайно:",
                    callback_data=CallbackData.TOGGLE_RANDOM
                ),
                InlineKeyboardButton(
                    UIConstants.CHECK_MARK if self._config.use_random_messages else UIConstants.CROSS_MARK,
                    callback_data=CallbackData.TOGGLE_RANDOM
                )
            )
            
            kb.add(InlineKeyboardButton("◀️ Назад", callback_data=f"{CBT.EDIT_PLUGIN}:{self._uuid}:0"))
            
            status = "🟢 Активен" if self._config.enabled else "🔴 Неактивен"
            text = (
                f"⚙️ Настройки спамера\n\n"
                f"Статус: {status}\n"
                f"⏱ Интервал: {self._config.interval_seconds} сек\n"
                f"📋 Чатов: {len(self._config.chat_ids)}\n"
                f"💬 Шаблонов: {len(self._config.message_templates)}\n"
                f"🎲 Faker: {UIConstants.CHECK_MARK if self._config.use_faker else UIConstants.CROSS_MARK}\n"
                f"🔀 Случайный выбор: {UIConstants.CHECK_MARK if self._config.use_random_messages else UIConstants.CROSS_MARK}"
            )
            
            self._bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.id,
                reply_markup=kb
            )
            self._bot.answer_callback_query(call.id)
        except Exception as e:
            logger.error(f"Error showing settings: {e}")

    def _toggle_enabled(self, call: CallbackQuery) -> None:
        try:
            self._config.update(enabled=not self._config.enabled)
            self._show_main_settings(call)
        except Exception as e:
            logger.error(f"Error toggling enabled: {e}")

    def _start_spam(self, call: CallbackQuery) -> None:
        try:
            self._on_start()
            self._bot.answer_callback_query(call.id, "▶️ Спамер запущен")
            self._show_main_settings(call)
        except Exception as e:
            logger.error(f"Error starting spam: {e}")
            self._bot.answer_callback_query(call.id, f"❌ Ошибка: {e}")

    def _stop_spam(self, call: CallbackQuery) -> None:
        try:
            self._on_stop()
            self._bot.answer_callback_query(call.id, "⏸️ Спамер остановлен")
            self._show_main_settings(call)
        except Exception as e:
            logger.error(f"Error stopping spam: {e}")

    def _request_interval(self, call: CallbackQuery) -> None:
        try:
            self._awaiting_interval.add(call.from_user.id)
            self._bot.send_message(
                call.message.chat.id,
                f"⏱ Текущий интервал: {self._config.interval_seconds} секунд\n\n"
                "Введите новый интервал (в секундах):"
            )
            self._bot.answer_callback_query(call.id)
        except Exception as e:
            logger.error(f"Error requesting interval: {e}")

    def _handle_interval_input(self, message: Message) -> None:
        try:
            self._awaiting_interval.discard(message.from_user.id)
            
            try:
                interval = int(message.text)
                if interval < 10:
                    raise ValueError("Too small")
            except ValueError:
                self._bot.reply_to(
                    message,
                    "❌ Ошибка: введите число больше 10"
                )
                return
            
            self._config.update(interval_seconds=interval)
            
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("◀️ К настройкам", callback_data=f"{CBT.PLUGIN_SETTINGS}:{self._uuid}"))
            
            self._bot.reply_to(
                message,
                f"✅ Интервал обновлен: {interval} сек",
                reply_markup=kb
            )
        except Exception as e:
            logger.error(f"Error handling interval: {e}")

    def _show_chats(self, call: CallbackQuery) -> None:
        try:
            kb = InlineKeyboardMarkup()
            
            kb.add(InlineKeyboardButton("➕ Добавить чат", callback_data=CallbackData.ADD_CHAT))
            kb.add(InlineKeyboardButton("➖ Удалить чат", callback_data=CallbackData.REMOVE_CHAT))
            
            kb.add(InlineKeyboardButton("◀️ Назад", callback_data=f"{CBT.PLUGIN_SETTINGS}:{self._uuid}"))
            
            chats_text = "\n".join([f"• {chat}" for chat in self._config.chat_ids]) if self._config.chat_ids else "Нет чатов"
            
            text = f"📋 Список чатов ({len(self._config.chat_ids)}):\n\n{chats_text}"
            
            self._bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.id,
                reply_markup=kb
            )
            self._bot.answer_callback_query(call.id)
        except Exception as e:
            logger.error(f"Error showing chats: {e}")

    def _request_add_chat(self, call: CallbackQuery) -> None:
        try:
            self._awaiting_chat.add(call.from_user.id)
            self._bot.send_message(
                call.message.chat.id,
                "📋 Введите ID чата для добавления:"
            )
            self._bot.answer_callback_query(call.id)
        except Exception as e:
            logger.error(f"Error requesting chat: {e}")

    def _handle_chat_input(self, message: Message) -> None:
        try:
            self._awaiting_chat.discard(message.from_user.id)
            
            chat_id = message.text.strip()
            self._config.add_chat_id(chat_id)
            
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("◀️ К чатам", callback_data=CallbackData.CHATS_LIST))
            
            self._bot.reply_to(
                message,
                f"✅ Чат добавлен: {chat_id}",
                reply_markup=kb
            )
        except Exception as e:
            logger.error(f"Error handling chat input: {e}")

    def _request_remove_chat(self, call: CallbackQuery) -> None:
        try:
            self._removal_chat_mode.add(call.from_user.id)
            
            chats_list = "\n".join([f"{i+1}. {chat}" for i, chat in enumerate(self._config.chat_ids)])
            self._bot.send_message(
                call.message.chat.id,
                f"📋 Введите номер чата для удаления:\n\n{chats_list}"
            )
            self._bot.answer_callback_query(call.id)
        except Exception as e:
            logger.error(f"Error requesting chat removal: {e}")

    def _handle_chat_removal(self, message: Message) -> None:
        try:
            self._removal_chat_mode.discard(message.from_user.id)
            
            try:
                index = int(message.text) - 1
                if 0 <= index < len(self._config.chat_ids):
                    removed_chat = self._config.chat_ids[index]
                    self._config.remove_chat_id(removed_chat)
                    
                    kb = InlineKeyboardMarkup()
                    kb.add(InlineKeyboardButton("◀️ К чатам", callback_data=CallbackData.CHATS_LIST))
                    
                    self._bot.reply_to(
                        message,
                        f"✅ Чат удален: {removed_chat}",
                        reply_markup=kb
                    )
                else:
                    self._bot.reply_to(message, "❌ Неверный номер")
            except ValueError:
                self._bot.reply_to(message, "❌ Введите число")
        except Exception as e:
            logger.error(f"Error handling chat removal: {e}")

    def _show_messages(self, call: CallbackQuery) -> None:
        try:
            kb = InlineKeyboardMarkup()
            
            kb.add(InlineKeyboardButton("➕ Добавить сообщение", callback_data=CallbackData.ADD_MESSAGE))
            kb.add(InlineKeyboardButton("➖ Удалить сообщение", callback_data=CallbackData.REMOVE_MESSAGE))
            
            kb.add(InlineKeyboardButton("◀️ Назад", callback_data=f"{CBT.PLUGIN_SETTINGS}:{self._uuid}"))
            
            messages_text = "\n\n".join([
                f"{i+1}. {msg[:50]}..." if len(msg) > 50 else f"{i+1}. {msg}"
                for i, msg in enumerate(self._config.message_templates)
            ]) if self._config.message_templates else "Нет шаблонов"
            
            text = f"💬 Шаблоны сообщений ({len(self._config.message_templates)}):\n\n{messages_text}"
            
            self._bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.id,
                reply_markup=kb
            )
            self._bot.answer_callback_query(call.id)
        except Exception as e:
            logger.error(f"Error showing messages: {e}")

    def _request_add_message(self, call: CallbackQuery) -> None:
        try:
            self._awaiting_message.add(call.from_user.id)
            self._bot.send_message(
                call.message.chat.id,
                "💬 Введите текст нового сообщения:"
            )
            self._bot.answer_callback_query(call.id)
        except Exception as e:
            logger.error(f"Error requesting message: {e}")

    def _handle_message_input(self, message: Message) -> None:
        try:
            self._awaiting_message.discard(message.from_user.id)
            
            self._config.add_message_template(message.text)
            
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("◀️ К сообщениям", callback_data=CallbackData.MESSAGES_LIST))
            
            self._bot.reply_to(
                message,
                "✅ Шаблон добавлен",
                reply_markup=kb
            )
        except Exception as e:
            logger.error(f"Error handling message input: {e}")

    def _request_remove_message(self, call: CallbackQuery) -> None:
        try:
            self._removal_message_mode.add(call.from_user.id)
            
            messages_list = "\n".join([
                f"{i+1}. {msg[:30]}..." if len(msg) > 30 else f"{i+1}. {msg}"
                for i, msg in enumerate(self._config.message_templates)
            ]) if self._config.message_templates else "Нет шаблонов"
            
            self._bot.send_message(
                call.message.chat.id,
                f"💬 Введите номер сообщения для удаления:\n\n{messages_list}"
            )
            self._bot.answer_callback_query(call.id)
        except Exception as e:
            logger.error(f"Error requesting message removal: {e}")

    def _handle_message_removal(self, message: Message) -> None:
        try:
            self._removal_message_mode.discard(message.from_user.id)
            
            try:
                index = int(message.text) - 1
                if 0 <= index < len(self._config.message_templates):
                    removed_msg = self._config.message_templates[index]
                    try:
                        self._config.remove_message_template(removed_msg)
                    except AttributeError:
                        try:
                            current = list(self._config.message_templates)
                            current.pop(index)
                            self._config.update(message_templates=current)
                        except Exception as exc:
                            logger.error(f"Failed to remove message template fallback: {exc}")
                            self._bot.reply_to(message, "❌ Не удалось удалить шаблон (внутренняя ошибка)")
                            return

                    kb = InlineKeyboardMarkup()
                    kb.add(InlineKeyboardButton("◀️ К сообщениям", callback_data=CallbackData.MESSAGES_LIST))
                    
                    self._bot.reply_to(
                        message,
                        "✅ Шаблон удалён",
                        reply_markup=kb
                    )
                else:
                    self._bot.reply_to(message, "❌ Неверный номер")
            except ValueError:
                self._bot.reply_to(message, "❌ Введите число")
        except Exception as e:
            logger.error(f"Error handling message removal: {e}")

    def _toggle_faker(self, call: CallbackQuery) -> None:
        try:
            try:
                self._config.update(use_faker=not self._config.use_faker)
            except Exception:
                try:
                    current = {
                        "interval_seconds": self._config.interval_seconds,
                        "enabled": self._config.enabled,
                        "chat_ids": list(self._config.chat_ids),
                        "message_templates": list(self._config.message_templates),
                        "use_faker": not getattr(self._config, "use_faker", False),
                        "use_random_messages": getattr(self._config, "use_random_messages", False),
                    }
                    self._config.update(**current)
                except Exception as exc:
                    logger.error(f"Failed to toggle faker via fallback: {exc}")

            self._show_main_settings(call)
            self._bot.answer_callback_query(call.id)
        except Exception as e:
            logger.error(f"Error toggling faker: {e}")

    def _toggle_random(self, call: CallbackQuery) -> None:
        try:
            try:
                self._config.update(use_random_messages=not self._config.use_random_messages)
            except Exception:
                try:
                    current = {
                        "interval_seconds": self._config.interval_seconds,
                        "enabled": self._config.enabled,
                        "chat_ids": list(self._config.chat_ids),
                        "message_templates": list(self._config.message_templates),
                        "use_faker": getattr(self._config, "use_faker", False),
                        "use_random_messages": not getattr(self._config, "use_random_messages", False),
                    }
                    self._config.update(**current)
                except Exception as exc:
                    logger.error(f"Failed to toggle random via fallback: {exc}")

            self._show_main_settings(call)
            self._bot.answer_callback_query(call.id)
        except Exception as e:
            logger.error(f"Error toggling random: {e}")
