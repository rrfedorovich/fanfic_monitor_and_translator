import logging
import os

from dataclasses import dataclass
from dotenv import load_dotenv
from typing import List


class BaseEnvHandler:
    """Базовый класс для обработки .env-файлов. Singleton."""

    _instance = None

    def __new__(cls, env_path: str):
        """
        env_path: Путь к файлу .env
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._env_path = env_path
        return cls._instance

    def load_env(self) -> bool:
        """Загружает переменные из .env в os.environ. Возвращает True, если файл .env корректен."""
        load_dotenv(self._env_path, override=True)
        return True

    def get_item(self, key) -> str:
        """Возвращает значение переменной окружения по ключу."""
        return os.getenv(key) or ""

    @property
    def env_path(self):
        """Возвращает путь к .env файлу."""
        return self._env_path

    @env_path.setter
    def env_path(self, path):
        """Устанавливает новый путь к .env файлу."""
        self._env_path = path
        self.load_env()


@dataclass
class EnvItem:
    """
    Класс для элементов env.
    name: str - имя.
    value: str - значение.
    description: str - русское пояснение.
    """

    name: str
    value: str
    description: str


class EnvHandler(BaseEnvHandler):
    """Класс для обработки .env. Singleton."""

    api_id = EnvItem("API_ID", "", "Ваш ID для API в телеграмме")
    api_hash = EnvItem("API_HASH", "", "Ваш Хэш для API в телеграмме")
    phone = EnvItem("PHONE", "", "Ваш телефон")
    fanfics_csv_path = EnvItem(
        "FANFICS_CSV_PATH", "", "Путь до .csv файла с фанфиками."
    )
    fanfics_out_dir = EnvItem(
        "FANFICS_OUT_DIR", "", "Путь до папки, куда сохранять фанфики"
    )
    telegram_on = EnvItem(
        "TELEGRAM_ON", "", "Включена ли отправка в телеграм: 1 - да, 0 - нет."
    )
    items = [
        telegram_on,
        api_id,
        api_hash,
        phone,
        fanfics_csv_path,
        fanfics_out_dir
    ]

    def load_env(self) -> bool:
        """Загружает переменные из .env в os.environ. Возвращает True, если файл .env корректен."""
        super().load_env()
        for item in self.items:
            item.value = self.get_item(item.name)
        if not all([i.value for i in self.items]):
            logging.info("Не заполнены все значения ENV.")
            return False
        return True

    def save_env(self):
        """Сохраняет изменения в env-файл."""
        with open(self.env_path, "w", encoding="utf-8") as f:
            for env_item in self.get_items():
                f.write(f"{env_item.name}='{env_item.value}'\n")

    def get_items(self) -> List[EnvItem]:
        """Возвращает список всех элементов."""
        return self.items
