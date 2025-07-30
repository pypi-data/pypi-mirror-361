import os
import logging

# Директория библиотеки (где находится этот скрипт)
LIB_DIR = os.path.dirname(os.path.abspath(__file__))

# Подпапка logs в корне библиотеки
LOG_DIR = os.path.join(LIB_DIR, "logs")

def setup_logging(log_file_name="library.log"):
    """
    Настраивает логирование с сохранением в logs/ и добавлением в файл (без перезаписи).
    
    Args:
        log_file_name (str): Имя лог-файла. По умолчанию — 'library.log'.
    
    Returns:
        logging.Logger: Готовый логгер.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, log_file_name)

    logger = logging.getLogger(f"LibraryLogger::{log_file_name}")
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Чтобы избежать дублирования логов в root-логгере

    # Очистим обработчики только если они уже были добавлены
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # 📂 Файл-лог (добавление в конец файла, а не перезапись)
    file_handler = logging.FileHandler(log_path, encoding='utf-8', mode='a')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 🖥 Консоль (для удобства отладки)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
