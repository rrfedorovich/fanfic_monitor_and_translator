import csv
import logging
import shutil
import sys

from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QTabWidget,
    QHBoxLayout,
    QTextEdit,
)
from PySide6.QtCore import Qt, QThread, Signal

from console import ENV, main


class LogWindow(QMainWindow):
    """Окно для отображения логов."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Отчет")
        self.setGeometry(100, 100, 600, 400)  # Положение и размер окна
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.setCentralWidget(self.log_text)  # Устанавливаем виджет в центр окна


class LoggingHandler(logging.Handler):
    """Обработчик логов для сигналов."""

    def __init__(self, signal: Signal) -> None:
        super().__init__()
        self.signal = signal

    def emit(self, record: logging.LogRecord) -> None:
        """Обработка сообщений из logging."""
        msg = self.format(record)
        self.signal.emit(msg)  # Отправляем лог через сигнал


class Worker(QThread):
    """Класс для параллельного запуска основной функции."""

    log_signal = Signal(str)  # Сигнал для передачи логов

    def __init__(self) -> None:
        super().__init__()


    def run(self) -> None:
        """Запускает функцию."""
        # Перенаправляем логи в сигнал
        # Создаём новый обработчик логов для этого воркера
        log_handler = LoggingHandler(self.log_signal)
        logging.getLogger().addHandler(log_handler)
        main()  # Выполняем долгую операцию
        # Удаляем обработчик после завершения работы
        logging.getLogger().removeHandler(log_handler)


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Переводчик фанфиков")  # Заголовок главного окна
        self.resize(1000, 600)  # Размер главного окна

        # Настройка логера: создаём окно для логов и настраиваем обработчик
        self.log_window = LogWindow()
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
        )
        
        # Главный layout: вкладки + кнопка запуска
        main_layout = QVBoxLayout()

        # Создаём вкладки для CSV и ENV редакторов
        tabs = QTabWidget()
        self.csv_table = self._set_csv(tabs)
        self.env_table = self._set_env(tabs)
        main_layout.addWidget(tabs)

        # Кнопка запуска функции (вне вкладок)
        self.run_button = QPushButton("Запустить перевод")
        self.run_button.setFixedHeight(35)
        self.run_button.clicked.connect(self.run_function)  # Привязываем обработчик
        # Добавляем на раскладку кнопку.
        main_layout.addWidget(self.run_button)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.load_env()
        self.load_csv()
        
        
    def _set_csv(self, tabs: QTabWidget) -> QTableWidget:
        """
        Устанавливает вкладку для чтения и редактирования .csv-файлов.
        Возвращает CSV-таблицу.
        
        tabs: QTabWidget - куда лепить вкладку.
        """
        # Таблица для редактирования CSV
        csv_table = QTableWidget(0, 3)
        csv_table.setHorizontalHeaderLabels(
            ["Название", "Адрес фанфика", "Номер последней главы"]
        )
        csv_table.setColumnWidth(0, 280)
        csv_table.setColumnWidth(1, 500)
        csv_table.setColumnWidth(2, 150)

        # Кнопки для работы с CSV
        csv_add_button = QPushButton("Добавить запись")
        csv_add_button.clicked.connect(self.add_csv_row)

        csv_save_button = QPushButton("Сохранить")
        csv_save_button.clicked.connect(self.save_csv)

        csv_delete_button = QPushButton("Удалить запись")
        csv_delete_button.clicked.connect(self.delete_csv_row)

        # Горизонтальный layout для кнопок
        csv_button_layout = QHBoxLayout()
        csv_button_layout.addWidget(csv_add_button)
        csv_button_layout.addWidget(csv_delete_button)
        csv_button_layout.addWidget(csv_save_button)

        # Добавляем таблицу и кнопки на вкладку CSV
        csv_layout = QVBoxLayout()  # Вертикальный layout для вкладки CSV
        csv_layout.addWidget(csv_table)
        csv_layout.addLayout(csv_button_layout)

        # Добавляем содержимое вкладки CSV на саму вкладку.
        csv_tab = QWidget()
        csv_tab.setLayout(csv_layout)
        tabs.addTab(csv_tab, "Фанфики")
        return csv_table

    def _set_env(self, tabs: QTabWidget) -> QTableWidget:
        """
        Устанавливает вкладку для чтения и редактирования .env-файлов.
        Возвращает ENV-таблицу.
        
        tabs: QTabWidget - куда лепить вкладку.
        """
        # Таблица для редактирования ENV
        env_table = QTableWidget(0, 2)
        env_table.setHorizontalHeaderLabels(["Параметр", "Значение"])
        env_table.setColumnWidth(0, 350)
        env_table.setColumnWidth(1, 585)

        # Кнопка для работы с ENV
        env_save_button = QPushButton("Сохранить")
        env_save_button.clicked.connect(self.save_env)  # Привязываем обработчик
        env_button_layout = QHBoxLayout()  # Горизонтальный layout для кнопок
        env_button_layout.addWidget(env_save_button)

        # Добавляем таблицу и кнопки на раскладку ENV
        env_layout = QVBoxLayout()  # Вертикальный layout для вкладки ENV
        env_layout.addWidget(env_table)
        env_layout.addLayout(env_button_layout)

        # Добавляем содержимое вкладки ENV на саму вкладку.
        env_tab = QWidget()
        env_tab.setLayout(env_layout)
        tabs.addTab(env_tab, "Настройки")
        return env_table

    def add_csv_row(self) -> None:
        """Добавляет строку в таблицу CSV."""
        row_pos = self.csv_table.rowCount()
        self.csv_table.insertRow(row_pos)
        for col in range(3):
            self.csv_table.setItem(row_pos, col, QTableWidgetItem(""))

    def delete_csv_row(self) -> None:
        """Удаление выбранной строки из таблицы."""
        selected_row = self.csv_table.currentRow()
        if selected_row >= 0:
            self.csv_table.removeRow(selected_row)
        else:
            logging.warning("Не выбрана строка для удаления.")

    def load_csv(self) -> None:
        """Считывание из CSV-файла данных в таблицу."""
        fanfics_path = Path(ENV.fanfics_csv_path.value)
        if not fanfics_path.exists():
            draft_fanfics_path = Path('./src/data/fanfics_example.csv')
            shutil.copy(draft_fanfics_path, fanfics_path)
        if ENV.load_env():
            with open(ENV.fanfics_csv_path.value, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=";")
                self.csv_table.setRowCount(0)
                next(reader)
                for row in reader:
                    row_pos = self.csv_table.rowCount()
                    self.csv_table.insertRow(row_pos)
                    for col, item in enumerate(row):
                        self.csv_table.setItem(row_pos, col, QTableWidgetItem(item))

    def save_csv(self) -> None:
        """Сохраняет данные из таблицы в CSV-файл."""
        if ENV.load_env():
            with open(
                ENV.fanfics_csv_path.value, "w", newline="", encoding="utf-8"
            ) as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Название", "URL", "Номер последней главы"])
                for row in range(self.csv_table.rowCount()):
                    row_data = []
                    for col in range(self.csv_table.columnCount()):
                        item = self.csv_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

    def load_env(self) -> None:
        """Считывание из ENV-файла данных в таблицу."""
        env_path = Path(ENV.env_path)
        if not env_path.exists():
            draft_env_path = Path('./src/data/.env_example')
            shutil.copy(draft_env_path, env_path)
        if ENV.load_env():
            self.env_table.setRowCount(0)
            for env_item in ENV.get_items():
                row_pos = self.env_table.rowCount()
                self.env_table.insertRow(row_pos)
                name_cell = QTableWidgetItem(env_item.description)
                # добавление флага запрета изменения
                name_cell.setFlags(name_cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.env_table.setItem(row_pos, 0, name_cell)
                self.env_table.setItem(row_pos, 1, QTableWidgetItem(env_item.value))

    def save_env(self) -> None:
        """Сохраняет данные из таблицы в env-файл"""
        for row, env_item in enumerate(ENV.get_items()):
            value = self.env_table.item(row, 1)
            if value is not None:
                env_item.value = value.text()
        ENV.save_env()
        ENV.load_env()
        self.load_csv()

    def run_function(self) -> None:
        """Запускает перевод и показывает окно с логами."""
        self.run_button.setEnabled(False)  # Блокируем кнопку на время выполнения
        self.log_window.show()  # Показываем окно с логами
        self.log_window.log_text.setText("")

        # Удаляем предыдущий воркер, если он существует
        if hasattr(self, "worker"):
            self.worker.log_signal.disconnect()
            self.worker.finished.disconnect()
            self.worker.quit()
            self.worker.wait()
            self.worker.deleteLater()

        # Создаём воркер и подключаем сигнал к обновлению QTextEdit
        self.worker = Worker()
        self.worker.log_signal.connect(self.log_window.log_text.append)
        self.worker.finished.connect(
            self.on_worker_finished
        )  # Подключаем обработчик завершения
        self.worker.start()

    def on_worker_finished(self) -> None:
        """Функция-обработчик завершения воркера."""
        self.load_csv()
        self.run_button.setEnabled(True)  # Разблокируем кнопку


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
