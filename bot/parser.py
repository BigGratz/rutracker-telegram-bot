import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict, Optional
import logging
from sqlalchemy import text
import brotli
import gzip
import zlib

from bot.config import config
from bot.database import Game, Settings, async_session

logger = logging.getLogger(__name__)

class RutrackerParser:
    def __init__(self):
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        
    async def create_session(self):
        """Создание aiohttp сессии"""
        connector = aiohttp.TCPConnector(limit=10, ssl=False)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout,
            headers=config.HEADERS
        )
    
    async def close_session(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Получение HTML страницы с поддержкой brotli"""
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                if response.status == 200:
                    # Получаем сырые байты
                    content = await response.read()
                    
                    # Пробуем декодировать с учетом content-encoding
                    encoding = response.headers.get('Content-Encoding', '').lower()
                    
                    try:
                        if 'br' in encoding:
                            content = brotli.decompress(content)
                        elif 'gzip' in encoding:
                            content = gzip.decompress(content)
                        elif 'deflate' in encoding:
                            content = zlib.decompress(content)
                    except Exception:
                        # Если декомпрессия не удалась, используем как есть
                        pass
                    
                    # Пробуем декодировать в строку
                    try:
                        return content.decode('windows-1251')
                    except UnicodeDecodeError:
                        try:
                            return content.decode('utf-8')
                        except UnicodeDecodeError:
                            return content.decode('utf-8', errors='ignore')
                else:
                    logger.error(f"Ошибка при запросе {url}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Ошибка при получении страницы {url}: {e}")
            return None
    
    def parse_forum_page(self, html: str) -> List[Dict]:
        """Парсинг страницы форума"""
        games = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Ищем таблицу с играми
            forum_table = soup.find('table', class_='vf-table')
            if not forum_table:
                logger.warning("Не найдена таблица vf-table")
                # Попробуем другой способ
                rows = soup.find_all('tr', class_='hl-tr')
            else:
                rows = forum_table.find_all('tr', class_='hl-tr')
            
            logger.info(f"Найдено {len(rows)} строк для обработки")
            
            for row in rows:
                try:
                    # Пропускаем строки без data-topic_id
                    if 'data-topic_id' not in row.attrs:
                        continue
                    
                    topic_id = int(row['data-topic_id'])
                    
                    # Пропускаем закрепленные темы (правила и важное)
                    icon_cell = row.find('td', class_='vf-col-icon')
                    if icon_cell:
                        icon = icon_cell.find('img')
                        if icon:
                            icon_src = icon.get('src', '')
                            if 'folder_sticky' in icon_src or 'folder_lock' in icon_src:
                                continue
                    
                    # Извлекаем заголовок
                    title_elem = row.find('a', class_='tt-text')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = f"https://rutracker.org/forum/viewtopic.php?t={topic_id}"
                    
                    # Извлекаем автора
                    author_elem = row.find('a', class_='topicAuthor')
                    author = author_elem.get_text(strip=True) if author_elem else "Неизвестно"
                    
                    # Извлекаем статистику торрента
                    torrent_elem = row.find('td', class_='vf-col-tor')
                    seeds = leeches = 0
                    size = "N/A"
                    
                    if torrent_elem:
                        # Сиды
                        seed_elem = torrent_elem.find('span', class_='seedmed')
                        if seed_elem:
                            seed_text = seed_elem.get_text(strip=True)
                            try:
                                seeds = int(re.sub(r'\D', '', seed_text))
                            except:
                                seeds = 0
                        
                        # Личи
                        leech_elem = torrent_elem.find('span', class_='leechmed')
                        if leech_elem:
                            leech_text = leech_elem.get_text(strip=True)
                            try:
                                leeches = int(re.sub(r'\D', '', leech_text))
                            except:
                                leeches = 0
                        
                        # Размер
                        size_elem = torrent_elem.find('a', class_='dl-stub')
                        if size_elem:
                            size = size_elem.get_text(strip=True)
                    
                    # Извлекаем количество ответов
                    replies_elem = row.find('td', class_='vf-col-replies')
                    replies = 0
                    downloads = 0
                    
                    if replies_elem:
                        # Ответы
                        replies_span = replies_elem.find('span')
                        if replies_span and 'title' in replies_span.attrs:
                            replies_text = replies_span['title'].replace('Ответов', '').strip()
                            try:
                                replies = int(replies_text)
                            except:
                                replies = 0
                        
                        # Скачивания
                        downloads_elems = replies_elem.find_all('p')
                        for elem in downloads_elems:
                            if 'Торрент скачан' in elem.get('title', ''):
                                downloads_b = elem.find('b')
                                if downloads_b:
                                    downloads_text = downloads_b.get_text(strip=True)
                                    # Удаляем запятые и точки
                                    downloads_text = downloads_text.replace(',', '').replace('.', '')
                                    try:
                                        downloads = int(re.sub(r'\D', '', downloads_text))
                                    except:
                                        downloads = 0
                                    break
                    
                    # Извлекаем дату последнего сообщения
                    date_elem = row.find('td', class_='vf-col-last-post')
                    last_post_date = None
                    
                    if date_elem:
                        date_ps = date_elem.find_all('p')
                        if date_ps and len(date_ps) > 0:
                            date_text = date_ps[0].get_text(strip=True)
                            try:
                                last_post_date = datetime.strptime(date_text, '%Y-%m-%d %H:%M')
                            except ValueError:
                                try:
                                    last_post_date = datetime.strptime(date_text, '%Y-%m-%d')
                                except:
                                    last_post_date = None
                    
                    games.append({
                        'topic_id': topic_id,
                        'title': title,
                        'url': url,
                        'author': author,
                        'size': size,
                        'seeds': seeds,
                        'leeches': leeches,
                        'replies': replies,
                        'downloads': downloads,
                        'last_post_date': last_post_date,
                        'genre': None,  # Эти поля будут заполнены при детальном парсинге
                        'languages': None,
                        'version': None,
                        'description': None
                    })
                    
                except Exception as e:
                    logger.warning(f"Ошибка при обработке строки: {e}")
                    continue
            
            return games
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге страницы: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    async def get_new_games(self) -> List[Dict]:
        """Получение списка новых игр"""
        await self.create_session()
        
        try:
            logger.info(f"Запрашиваю страницу: {config.RUTRACKER_URL}")
            html = await self.fetch_page(config.RUTRACKER_URL)
            
            if not html:
                logger.error("Не удалось получить HTML страницы")
                return []
            
            logger.info(f"Получено {len(html)} символов HTML")
            games = self.parse_forum_page(html)
            logger.info(f"Найдено {len(games)} игр на странице")
            
            if not games:
                logger.info("Игр на странице не найдено")
                return []
            
            # Получаем последний проверенный topic_id из базы
            async with async_session() as session:
                settings_result = await session.execute(
                    text("SELECT value FROM settings WHERE key = 'last_topic_id'")
                )
                last_topic_setting = settings_result.scalar_one_or_none()
                
                if last_topic_setting:
                    try:
                        last_topic_id = int(last_topic_setting)
                    except ValueError:
                        last_topic_id = 0
                    
                    logger.info(f"Последний проверенный topic_id: {last_topic_id}")
                    
                    # Фильтруем только новые игры (с topic_id больше последнего)
                    new_games = [g for g in games if g['topic_id'] > last_topic_id]
                    
                    if new_games:
                        # Сортируем по topic_id (по возрастанию)
                        new_games.sort(key=lambda x: x['topic_id'])
                        
                        # Обновляем последний topic_id (берем максимальный)
                        new_last_id = max(g['topic_id'] for g in new_games)
                        
                        await session.execute(
                            text("UPDATE settings SET value = :value WHERE key = 'last_topic_id'"),
                            {"value": str(new_last_id)}
                        )
                        await session.commit()
                        logger.info(f"Обновлен last_topic_id: {new_last_id}")
                    
                    logger.info(f"Найдено {len(new_games)} новых игр")
                    return new_games
                else:
                    # Если настройки нет, сохраняем максимальный topic_id
                    max_id = max(g['topic_id'] for g in games) if games else 0
                    setting = Settings(key='last_topic_id', value=str(max_id))
                    session.add(setting)
                    await session.commit()
                    logger.info(f"Создана новая запись last_topic_id: {max_id}")
                    
                    return []  # Первый запуск - не отправляем уведомления
            
        except Exception as e:
            logger.error(f"Ошибка в get_new_games: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
        finally:
            await self.close_session()
