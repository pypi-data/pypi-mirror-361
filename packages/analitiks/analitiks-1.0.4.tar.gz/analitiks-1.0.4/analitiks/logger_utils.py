import os
import logging

# 📍 Задаём путь к логам (в корне библиотеки)
LOG_DIR = r"C:\Python_lib\analitiks\logs"

def setup_logging(log_file_name="library.log"):
    """
    Настраивает логирование с сохранением в C:\Python_lib\analitiks\logs\ и добавлением в файл (без перезаписи).
    
    Args:
        log_file_name (str): Имя лог-файла. По умолчанию — 'library.log'.
    
    Returns:
        logging.Logger: Готовый логгер.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, log_file_name)

    logger = logging.getLogger(f"analitiks::{log_file_name}")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    file_handler = logging.FileHandler(log_path, encoding='utf-8', mode='a')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
