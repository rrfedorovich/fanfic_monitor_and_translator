import logging
from typing import List

from telethon.sync import TelegramClient


class TelegramExporter:
    """Класс для отправки файлов в телеграмм в избранное."""

    # Убираем лишний вывод информации
    logging.getLogger("telethon").setLevel(logging.CRITICAL)

    def __init__(self, api_id: int, api_hash: str, phone: str) -> None:
        """
        api_id: ID приложения телеграма.
        api_hash: Хэш приложения телеграма.
        phone: Номер телефона.
        """
        self.api_id: int = api_id
        self.api_hash: str = api_hash
        self.phone: str = phone

    async def send_file_to_telegram(self, file_pathes: List[str], message: str):
        """Отправка файлов в телеграмм в избранное."""
        logging.info("---")
        logging.info("> Отправка в телеграм...")
        logging.info(">> Соединение.")
        client = TelegramClient("session_name", self.api_id, self.api_hash)
        await client.start(self.phone)

        logging.info(">> Отправка...")
        await client.send_message("me", message)
        await client.send_file("me", file_pathes)

        logging.info(">>> ... успешна.")
        await client.disconnect()
        logging.info(">> Отключение.")
