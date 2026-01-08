import unittest
import shutil
import os

from src.modules.csv_handler import CSVHandler


class TestCSVHandler(unittest.TestCase):
    """Класс для тестирования обработчика .csv-файлов."""

    def test_read_csv(self):
        """Тестирование чтения."""
        fanfics = [
            [
                "Название фанфика 1",
                "Адрес фанфика 1",
                "1",
            ]
        ]
        csv_handler = CSVHandler("./tests/modules/csv_handler/test.csv")
        self.assertEqual(fanfics, csv_handler.read_csv())

    def test_write_csv(self):
        """Тестирование записи."""
        shutil.copy(
            "./tests/modules/csv_handler/test.csv", "./tests/modules/csv_handler/test2.csv"
        )
        csv_handler = CSVHandler("./tests/modules/csv_handler/test2.csv")
        data = csv_handler.read_csv()
        data[0][2] = "101"
        csv_handler.write_csv(data)
        self.assertEqual(data, csv_handler.read_csv())
        os.remove("./tests/modules/csv_handler/test2.csv")
