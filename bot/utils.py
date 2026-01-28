import re
from datetime import datetime
from typing import Optional

def extract_topic_id(url: str) -> Optional[int]:
    """Извлечение ID темы из URL"""
    match = re.search(r't=(\d+)', url)
    if match:
        return int(match.group(1))
    return None

def format_size(size_str: str) -> str:
    """Форматирование размера файла"""
    if not size_str:
        return "N/A"
    
    # Убираем лишние пробелы
    size_str = size_str.strip()
    
    # Если размер уже в читаемом формате, возвращаем как есть
    if any(unit in size_str.upper() for unit in ['KB', 'MB', 'GB', 'TB']):
        return size_str
    
    try:
        # Пытаемся конвертировать байты в читаемый формат
        size_bytes = float(size_str)
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
    except:
        pass
    
    return size_str

def parse_date(date_str: str) -> Optional[datetime]:
    """Парсинг даты из строки"""
    formats = [
        '%Y-%m-%d %H:%M',
        '%d-%b-%y %H:%M',
        '%d.%m.%Y %H:%M',
        '%d/%m/%Y %H:%M'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def clean_html(text: str) -> str:
    """Очистка HTML тегов из текста"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def truncate_text(text: str, max_length: int = 500, ellipsis: str = "...") -> str:
    """Обрезка текста с добавлением многоточия"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(ellipsis)] + ellipsis
