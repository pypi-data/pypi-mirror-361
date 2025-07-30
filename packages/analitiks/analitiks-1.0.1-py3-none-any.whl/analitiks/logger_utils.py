import os
import logging

# Получаем директорию библиотеки
LIB_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(LIB_DIR, "logs")

def setup_logging(log_file_name="library.log"):
    """
    Настройка логирования с сохранением в папку logs в директории библиотеки.
    
    Args:
        log_file_name (str): Имя файла логов (по умолчанию 'library.log').
    
    Returns:
        logging.Logger: Логгер для использования в функциях.
    """
    # Создаем папку logs, если ее нет
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Полный путь к файлу логов
    log_file = os.path.join(LOG_DIR, log_file_name)
    
    # Настройка логгера
    logger = logging.getLogger("LibraryLogger")
    logger.setLevel(logging.INFO)
    
    # Удаляем старые обработчики, если они есть, чтобы избежать дублирования
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Формат логов
    log_format = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    # Обработчик для файла
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    
    return logger