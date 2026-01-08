import itertools
import logging
import re
import time

from typing import List, Iterator

from deep_translator import GoogleTranslator


class Translator:
    """Класс для перевода текста с английского на русский."""

    def __init__(
        self, batch_size: int = 5, log_prefix: str = ">", max_retries: int = 3
    ) -> None:
        """
        Инициализатор.

        Параметры:
            batch_size: int - максимальное количество одновременно переводимых
                              блоков текста (блок <= 5k символов). Больше - быстрее.
            log_prefix: str - префикс для сообщений логов.
            max_retries: int - максимальное число попыток перевода участка текста.
        """

        self._batch_size: int = batch_size
        self._translator: GoogleTranslator = GoogleTranslator(source="en", target="ru")
        self._log_prefix: str = log_prefix
        self._max_retries: int = max_retries

    def _prepare(self, text: str) -> Iterator[str]:
        """
        Разбивает текст на блоки не больше 5k символов.

        Параметры:
            text: str - текст, который нужно разбить на блоки.

        Возвращает:
            : Iterator[str] - последовательность блоков текста, каждый не длиннее 5k символов.
        """

        tmp = ""
        for paragraph in text.split("\n"):
            if len(paragraph) + len(tmp) + 2 >= 5000:
                yield tmp[:-1]
                tmp = ""
            tmp += paragraph + "\n"
        yield tmp[:-1]

    def _get_batches(self, title: str, blocks: Iterator[str]) -> Iterator[List[str]]:
        """
        Создает порции блоков не длиннее 5k символов.
        В начале ставит title, затем разбивает blocks на списки блоков текста,
        каждый блок не длиннее 5k символов.
        Количество блоков в каждом списке(порции): не больше self._batch_size.

        Параметры:
            title: str - название главы.
            blocks:Iterator[str] - последовательность блоков текста, каждый блок длинной
                                   не больше 5k символов.

        Возвращает:
            : Iterator[List[str]] - последовательность списков по self._batch_size (и меньше)
                                    блоков текста не длиннее 5k символов.
        """
        blocks = itertools.chain([title], blocks)
        batch: List[str] = []
        for i, text in enumerate(blocks):
            batch.append(text)
            if (i + 1) % self._batch_size == 0:
                yield batch
                batch = []
        if batch:
            yield batch

    def _translate(self, title: str, text: str) -> List[str] | None:
        """
        Перевод текста по фрагментам с обработкой ошибок и повторными попытками.

        Параметры:
            title: str - название главы.
            text: str - текст главы.

        Возворащает:
            : List[str] - переведенные название и текст главы.
            : None - если возникли проблемы с переводом.
        """
        batches_iterator = self._get_batches(title, self._prepare(text))
        len_of_translated = -len("\n")
        len_of_text_and_title = len(text) + len(title)

        logging.info(f"{self._log_prefix}> Длина текста: {len(text)} символов.")

        translated_title: str = ""
        translated_text: str = ""

        for index, batch in enumerate(batches_iterator):
            retries = 0
            success = False

            while retries < self._max_retries and not success:
                try:
                    blocks_sizes = [len(i) for i in batch]
                    translated_batch = self._translator.translate_batch(batch)
                    if index == 0:
                        translated_title = translated_batch[0]
                        len_of_translated += blocks_sizes[0]

                        translated_batch = translated_batch[1:]
                        blocks_sizes = blocks_sizes[1:]

                    translated_text += "\n".join(translated_batch)
                    len_of_translated += sum(blocks_sizes) + len("\n") * (
                        len(blocks_sizes)
                    )

                    logging.info(
                        f"{self._log_prefix}> Переведено: {int(len_of_translated/len_of_text_and_title*100)}%."
                    )
                    success = True

                except Exception as e:
                    retries += 1
                    logging.error(f"{self._log_prefix}> Ошибка при переводе: {e}.")
                    logging.error(
                        f"{self._log_prefix}> Попытка {retries} из {self._max_retries}."
                    )
                    if retries < self._max_retries:
                        time.sleep(10)  # Ожидание 10 секунд перед повторной попыткой
                    else:
                        logging.error(
                            f"{self._log_prefix}> Превышено максимальное количество попыток. Остановка программы."
                        )
                        return None

        return [translated_title, translated_text]

    def run(
        self, title: str, text: str, description: str = "Перевод..."
    ) -> List[str] | None:
        """
        Запускает перевод.

        Параметры:
            title: str - название главы.
            text: str - текст главы.
            description: str - краткое текстовое приветствие-описание для системы логирования
                               (на логику не влияет).

        Возворащает:
            : str - переведенный текст
            : None - если возникли проблемы с переводом.
        """

        logging.info("---")
        logging.info(f"{self._log_prefix} {description}")
        return self._translate(title, text)
