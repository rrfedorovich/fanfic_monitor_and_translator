import abc
import logging
import time
from typing import List

import requests
from bs4 import BeautifulSoup, Tag


class Chapter:
    """Класс для обработки глав."""

    def __init__(self, title: str, text: str, number: int) -> None:
        self.title: str = title
        self.text: str = text
        self.number: int = number

    def __repr__(self) -> str:
        """Удобный вывод."""
        return f"{self.title[:30]} | {self.text[:40]}"


class GetData(abc.ABC):
    """Класс для получения данных из интернета."""

    @staticmethod
    def _do_wait_do(func):
        """Декоратор: повторяет, пока не получится."""

        def wrap(self, *args, **kwargs):
            k = 3
            response = None
            while k > 0:
                try:
                    response = func(self, *args, **kwargs)
                    break
                except Exception as e:
                    k -= 1
                    logging.error(f">> {e}")
                    if k > 0:
                        time.sleep(10)
                    else:
                        logging.error("")
                        return None
            return response

        return wrap

    @staticmethod
    @_do_wait_do
    def get_data(url) -> requests.Response:
        """Безопасно запрашивает данные."""
        return requests.get(url)


class BaseSite(abc.ABC):
    """Класс-шаблон для получения фанфиков с сайтов."""

    def __init__(self, name: str, url: str, last_chapter: str) -> None:
        """
        name: Название фанфика для пользователя.
        url: Адрес фанфика.
        last_chapter: Номер последней главы.
        """
        self.name: str = name
        self.url: str = url
        self.last_chapter: int = int(last_chapter)

        self._new_chapters: List[Chapter] = []
        self.fic_url: str = url

    def __repr__(self) -> str:
        """Удобный вывод на печать."""
        return " | ".join(self.get_data_for_csv())

    def get_data_for_csv(self) -> List[str]:
        """Выгрузка данных для CSV."""
        return [self.name, self.url, str(self.last_chapter)]

    def get_update(self) -> None:
        """Загрузка новых глав и обновление текущей переменной фанфика."""
        self._new_chapters = self.get_chapters_startwith(self.last_chapter + 1)
        self.last_chapter += len(self._new_chapters)

    def export_new_chapters(self) -> List[Chapter]:
        """Выгрузка новых глав."""
        return self._new_chapters

    @abc.abstractmethod
    def get_chapters_startwith(self, start_chapter: int) -> List[Chapter]:
        """Получает главы с указанной."""
        logging.info("---")
        logging.info("> Скачивание...")
        logging.info(f"> Получение глав начиная с {start_chapter}...")


class SpaceBattles(GetData, BaseSite):
    """Класс для получения фанфиков из SpaceBattles."""

    def __init__(self, name: str, url: str, last_chapter: str) -> None:
        """
        name: Название фанфика для пользователя.
        url: Адрес фанфика.
        last_chapter: Номер последней главы.
        """
        super().__init__(name, url, last_chapter)
        self.fic_url: str = "/".join(url.split("/")[:5]) + "/"

    def get_chapters_startwith(self, start_chapter: int) -> List[Chapter]:
        """
        Получает главы с указанной через режим readmode.
        Нумерация глав начинается с 1.
        """
        super().get_chapters_startwith(start_chapter)
        chapters = []
        chapter_id = start_chapter
        page = 1 + (start_chapter - 1) // 10
        start_chapter -= (page - 1) * 10 + 1
        count_of_pages = None

        while count_of_pages is None or page <= count_of_pages:
            response = self.get_data(self.fic_url + f"reader/page-{page}")
            if response:
                html = BeautifulSoup(response.content, "html.parser")
                if count_of_pages is None:
                    count_of_pages = self.get_count_of_pages(html)
                    if count_of_pages is None or page > count_of_pages:
                        break
                page += 1
                articles = html.select("article.js-post")
                for chapter_tag in articles[start_chapter:]:
                    chapter = self.handle_chapter(chapter_tag, chapter_id)
                    if chapter:
                        chapters.append(chapter)
                        chapter_id += 1
                    else:
                        break
                start_chapter = 0
            else:
                logging.error(">> Не смог загрузить фанфик.")
                break
        return chapters

    def handle_chapter(self, chapter: Tag, chapter_id: int) -> None | Chapter:
        """
        Обработка главы.
        Возвращает обработанную главу или None, если не получилось.
        """
        logging.info(f">> Получение главы {chapter_id}")
        title_block = chapter.select_one("span span")
        text_block = chapter.select_one(".message-content.js-messageContent")
        if title_block is not None and text_block is not None:
            title = title_block.get_text()
            text = text_block.get_text()
            return Chapter(title, text, chapter_id)
        else:
            logging.error(">>> Не смог определить содержимое главы.")
            return None

    def get_count_of_pages(self, html: Tag) -> int | None:
        """Возвращает либо количество страниц, либо None, если не получилось определить."""
        pages_block = html.select_one(".pageNav-main li:last-child a")
        if pages_block is not None:
            return int(pages_block.get_text())
        else:
            logging.error(">> Не смог определить номер последней страницы.")
            return None


class SufficientVelocity(SpaceBattles):
    """Класс для получения фанфиков из SufficientVelocity."""

    pass


class FanficFactory:
    """Фабрика для генерации экземляров подходящих под URL классов-обработчиков сайтов."""

    @staticmethod
    def get_fanfic(name: str, url: str, last_chapter: str) -> BaseSite | None:
        """
        Возвращает экземпляр одного из классов-обработчиков сайтов.

        name: Название фанфика для пользователя.
        url: Адрес фанфика.
        last_chapter: Номер последней главы.
        """
        if "spacebattles" in url:
            return SpaceBattles(name, url, last_chapter)
        elif "sufficientvelocity" in url:
            return SufficientVelocity(name, url, last_chapter)
        return None
