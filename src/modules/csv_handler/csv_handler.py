import csv
from typing import List


class CSVHandler:
    """Обработчик CSV-файлов."""

    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path

    def read_csv(self) -> List[List[str]]:
        """Читает CSV-файл и возвращает список объектов Fanfic."""
        with open(self.file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=";")
            field_names = next(reader)
            return [row for row in reader]

    def write_csv(self, fanfics: List[List[str]]):
        """Записывает данные в CSV-файл."""
        with open(self.file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=";")
            field_names = next(reader)
        with open(self.file_path, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(field_names)
            writer.writerows(fanfics)
