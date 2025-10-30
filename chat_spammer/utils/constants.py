from dataclasses import dataclass


@dataclass(frozen=True)
class PluginMetadata:
    NAME: str = "ChatSpammer"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = (
        "Автоматическая отправка сообщений в чаты FunPay.\n\n"
        "Возможности:\n"
        "- Настройка списка чатов\n"
        "- Множество шаблонов сообщений\n"
        "- Генерация случайных сообщений (Faker)\n"
        "- Гибкая настройка интервалов\n"
        "- Telegram управление\n\n"
        "v1.0.0 - Полный рефакторинг"
    )
    CREDITS: str = "@useanasha | @prince4scale"
    UUID: str = "b15ccbb6-30a1-4524-b0fe-cc23cc5771ae"


@dataclass(frozen=True)
class UIConstants:
    CHECK_MARK: str = "✅"
    CROSS_MARK: str = "❌"
    PLAY: str = "▶️"
    STOP: str = "⏸️"


@dataclass(frozen=True)
class CallbackData:
    TOGGLE: str = "CS_TOGGLE"
    START: str = "CS_START"
    STOP: str = "CS_STOP"
    INTERVAL: str = "CS_INTERVAL"
    CHATS_LIST: str = "CS_CHATS_LIST"
    ADD_CHAT: str = "CS_ADD_CHAT"
    REMOVE_CHAT: str = "CS_REMOVE_CHAT"
    MESSAGES_LIST: str = "CS_MSGS_LIST"
    ADD_MESSAGE: str = "CS_ADD_MSG"
    REMOVE_MESSAGE: str = "CS_REMOVE_MSG"
    TOGGLE_FAKER: str = "CS_FAKER"
    TOGGLE_RANDOM: str = "CS_RANDOM"