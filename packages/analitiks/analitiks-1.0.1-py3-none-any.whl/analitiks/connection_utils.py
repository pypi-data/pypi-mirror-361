import socket
import re
import os
from .logger_utils import setup_logging

def read_file_contents(file_path):
    """
    Читает содержимое файла и заменяет хост на localhost в строке подключения, если он совпадает с текущим хостом или IP.
    Если файл не содержит строки подключения, возвращает его содержимое без изменений.
    
    Args:
        file_path (str): Путь к файлу.
    
    Returns:
        str: Обработанное содержимое файла или сообщение об ошибке.
    """
    logger = setup_logging(log_file_name="connection_utils.log")
    
    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()
        
        # Получаем имя хоста, полное доменное имя и IP текущего сервера
        current_host = socket.gethostname().lower()
        current_fqdn = socket.getfqdn().lower()
        try:
            current_ip = socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            current_ip = None
        
        # Извлекаем хост из строки подключения, если он есть
        host_match = re.search(r'@([^\s:\/]+)(?::\d+)?/', file_contents)
        if host_match:
            connection_host = host_match.group(1).lower()
            
            # Условия для замены хоста на localhost
            if (current_host == connection_host or 
                current_fqdn == connection_host or 
                #connection_host.startswith('rdsh-02a') or 
                #connection_host == 'rdsh-02a.ad.massovka.site' or 
                (current_ip and current_ip == connection_host)):
                logger.info(f"Заменен хост {connection_host} на localhost в файле {os.path.basename(file_path)}")
                file_contents = re.sub(r'@' + re.escape(connection_host) + r'(:?\d*/|/)', '@localhost\\1', file_contents)
        
        return file_contents
    except FileNotFoundError:
        logger.error(f"Файл '{file_path}' не найден.")
        return f"Файл '{file_path}' не найден."
    except Exception as e:
        logger.error(f"Ошибка при чтении файла '{file_path}': {str(e)}")
        return f"Ошибка при чтении файла '{file_path}': {str(e)}"