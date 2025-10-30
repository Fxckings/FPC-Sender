from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Any
from pathlib import Path
import json
import logging

logger = logging.getLogger("FPC.ChatSpammer.Config")


@dataclass
class SpammerConfig:
    enabled: bool = False
    interval_seconds: int = 1000
    startup_delay: int = 15
    chat_ids: List[str] = field(default_factory=lambda: [
        "flood",
        "game-41",
        "game-2",
        "game-3",
        "game-4",
        "game-5",
        "game-123"
    ])
    message_templates: List[str] = field(default_factory=lambda: [
        "Привет! Как дела?",
        "Как ваши дела?",
        "Эх, как же хочется поиграть!",
    ])
    use_random_messages: bool = True
    use_faker: bool = False
    notify_on_error: bool = True
    
    _config_path: Path = field(default=Path("storage/plugins/chat_spammer.json"), init=False)

    @classmethod
    def load(cls) -> SpammerConfig:
        config_path = Path("storage/plugins/chat_spammer.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    instance = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
                    instance._config_path = config_path
                    logger.info("Configuration loaded")
                    return instance
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        
        instance = cls()
        instance._config_path = config_path
        instance.save()
        return instance

    def save(self) -> None:
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            data = {k: v for k, v in asdict(self).items() if not k.startswith("_")}
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.debug("Configuration saved")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def update(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()

    def add_chat_id(self, chat_id: str) -> None:
        if chat_id not in self.chat_ids:
            self.chat_ids.append(chat_id)
            self.save()

    def remove_chat_id(self, chat_id: str) -> None:
        if chat_id in self.chat_ids:
            self.chat_ids.remove(chat_id)
            self.save()

    def add_message_template(self, template: str) -> None:
        if template not in self.message_templates:
            self.message_templates.append(template)
            self.save()

    def remove_message_template(self, index: int) -> None:
        if 0 <= index < len(self.message_templates):
            self.message_templates.pop(index)
            self.save()