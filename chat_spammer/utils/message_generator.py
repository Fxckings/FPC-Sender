from __future__ import annotations
from typing import Optional
import random
import logging

try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False

from ..core.config import SpammerConfig

logger = logging.getLogger("FPC.ChatSpammer.MessageGen")


class MessageGenerator:
    def __init__(self, config: SpammerConfig):
        self._config = config
        self._faker: Optional[Faker] = None
        
        if FAKER_AVAILABLE and config.use_faker:
            try:
                self._faker = Faker("ru_RU")
                logger.info("Faker initialized")
            except Exception as e:
                logger.warning(f"Failed to init Faker: {e}")

    def generate(self) -> str:
        if self._config.use_faker and self._faker:
            return self._generate_faker_message()
        
        if self._config.use_random_messages and self._config.message_templates:
            return random.choice(self._config.message_templates)
        
        if self._config.message_templates:
            return self._config.message_templates[0]
        
        return "Привет!"

    def _generate_faker_message(self) -> str:
        if not self._faker:
            return self.generate()

        templates = [
            lambda: self._faker.sentence(nb_words=12),
            lambda: f"{self._faker.catch_phrase()} 🎮",
            lambda: f"{self._faker.bs().capitalize()}!",
            lambda: f"Специальное предложение: {self._faker.word()}!"
        ]
        
        try:
            return random.choice(templates)()
        except Exception as e:
            logger.error(f"Error generating Faker message: {e}")
            return "Привет!"