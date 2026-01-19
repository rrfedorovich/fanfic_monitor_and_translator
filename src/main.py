import asyncio
import logging

from pathlib import Path
from typing import List

from simplest_epub_generator import Chapter as ChapterEpub, Epub as BookEpub

from modules.csv_handler import CSVHandler
from modules.env_handler import EnvHandler
from modules.fanfic import Chapter, FanficFactory
from modules.output_handler import TelegramExporter
from modules.translator import Translator

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
ENV = EnvHandler("./setting/.env")


def main():
    """Запуск кода."""
    if ENV.load_env():  # Если заданы все значения.
        error_flag: bool = False
        
        FANFICS_OUT_DIR = Path(ENV.fanfics_out_dir.value)

        csv_base = CSVHandler(ENV.fanfics_csv_path.value)
        tr = Translator(batch_size=10)
        telegram_exporter = TelegramExporter(
            int(ENV.api_id.value), ENV.api_hash.value, ENV.phone.value
        )
        
        fanfics_or_None = [FanficFactory.get_fanfic(*row) for row in csv_base.read_csv()]
        fanfics = [fanfic for fanfic in fanfics_or_None if fanfic is not None]
        updated_rows_for_csv = [fanfic.get_data_for_csv() for fanfic in fanfics]

        for index_ff, ff in enumerate(fanfics):
            logging.info("---")
            logging.info(f"<<< {ff.name} >>>")
            
            file_name: str = f"{ff.name}_{ff.last_chapter+1}"
            ff.get_update()
            file_name += f"-{ff.last_chapter}.epub"
            file_path = FANFICS_OUT_DIR / ff.name / file_name

            new_chapters: List[Chapter] = ff.export_new_chapters()
            if new_chapters:
                for chapter in new_chapters:
                    translated = tr.run(chapter.title, chapter.text, f'Перевод главы {chapter.number}.')
                    if translated is not None:
                        chapter.title, chapter.text = translated
                    else:
                        logging.info("---")
                        logging.info("Операция остановлена из-за проблем с переводом.")
                        error_flag = True
                        break
                if not error_flag:
                    epub_chapters = [ChapterEpub(ch.title, ch.text) for ch in new_chapters]
                    book = BookEpub(ff.name, "ru")
                    book.add_chapters(epub_chapters)
                    book.write_file(file_path)
                    logging.info("---")
                    logging.info(f"> Файл записан.")
                    logging.info(f">> {file_path}")
                    
                    asyncio.run(
                        telegram_exporter.send_file_to_telegram(
                            [str(file_path.absolute())], ff.name
                        )
                    )

                    updated_rows_for_csv[index_ff] = ff.get_data_for_csv()
                    csv_base.write_csv(updated_rows_for_csv)
            if error_flag:
                break
        if not error_flag:
            logging.info("---")
            logging.info("<<< Завершено >>>")


if __name__ == "__main__":
    main()
