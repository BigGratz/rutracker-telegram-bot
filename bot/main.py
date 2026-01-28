import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import text
import html
from datetime import datetime

from bot.config import config
from bot.parser import RutrackerParser
from bot.database import Game, Settings, init_db, async_session

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Инициализация планировщика
scheduler = AsyncIOScheduler()
parser = RutrackerParser()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("Извините, у вас нет доступа к этому боту.")
        return
    
    await message.answer(
        "👋 <b>Привет! Я бот для отслеживания новых игр на RuTracker.</b>\n\n"
        "<b>Доступные команды:</b>\n"
        "/start - Запуск бота\n"
        "/status - Статус работы\n"
        "/check_now - Проверить новые игры сейчас\n"
        "/stats - Статистика\n"
        "/last - Последние найденные игры\n"
        "/help - Помощь\n\n"
        f"<b>Ваш ID:</b> {message.from_user.id}\n"
        f"<b>Автопроверка:</b> каждые {config.CHECK_INTERVAL//60} минут",
        parse_mode='HTML'
    )

# Команда /status
@dp.message(Command("status"))
async def cmd_status(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    jobs = scheduler.get_jobs()
    job_status = "активна" if jobs and jobs[0].next_run_time else "не активна"
    
    status_text = (
        f"🤖 <b>Статус бота:</b> Работает\n"
        f"📊 <b>Запланированные задачи:</b> {len(jobs)}\n"
        f"⏰ <b>Интервал проверки:</b> {config.CHECK_INTERVAL} секунд\n"
        f"🔍 <b>Автопроверка:</b> {job_status}\n"
        f"🎯 <b>Отслеживаемый раздел:</b>\n{config.RUTRACKER_URL}"
    )
    
    await message.answer(status_text, parse_mode='HTML')

# Команда /check_now
@dp.message(Command("check_now"))
async def cmd_check_now(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    await message.answer("🔍 Начинаю проверку новых игр...")
    await check_new_games()

# Команда /stats
@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    async with async_session() as session:
        try:
            # Получаем статистику из базы
            games_count = await session.execute(text("SELECT COUNT(*) FROM games"))
            games_count = games_count.scalar() or 0
            
            notified_count = await session.execute(text("SELECT COUNT(*) FROM games WHERE is_notified = 1"))
            notified_count = notified_count.scalar() or 0
            
            last_check = await session.execute(
                text("SELECT value FROM settings WHERE key = 'last_check'")
            )
            last_check_result = last_check.scalar_one_or_none()
            
            last_topic = await session.execute(
                text("SELECT value FROM settings WHERE key = 'last_topic_id'")
            )
            last_topic_result = last_topic.scalar_one_or_none() or "не установлен"
            
            stats_text = (
                f"📊 <b>Статистика базы данных:</b>\n"
                f"🎮 <b>Всего игр:</b> {games_count}\n"
                f"🔔 <b>Уведомлено:</b> {notified_count}\n"
                f"🆔 <b>Последний topic_id:</b> {last_topic_result}\n"
                f"🕐 <b>Последняя проверка:</b> {last_check_result or 'Не проводилась'}"
            )
            
            await message.answer(stats_text, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            await message.answer(f"❌ Ошибка при получении статистики: {e}")

# Команда /last
@dp.message(Command("last"))
async def cmd_last(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    async with async_session() as session:
        try:
            result = await session.execute(
                text("SELECT * FROM games ORDER BY created_date DESC LIMIT 5")
            )
            last_games = result.fetchall()
            
            if not last_games:
                await message.answer("📭 В базе данных пока нет игр.")
                return
            
            response = "🎮 <b>Последние 5 игр в базе:</b>\n\n"
            
            for i, game in enumerate(last_games, 1):
                # Форматируем дату
                date_str = game.created_date
                if isinstance(date_str, str):
                    try:
                        # Пытаемся парсить строку
                        if 'T' in date_str:
                            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        else:
                            dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        date_display = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        date_display = date_str[:16]
                elif hasattr(game.created_date, 'strftime'):
                    date_display = game.created_date.strftime('%Y-%m-%d %H:%M')
                else:
                    date_display = str(game.created_date)[:16]
                
                response += (
                    f"<b>{i}. {html.escape(game.title)}</b>\n"
                    f"   👤 <i>Автор:</i> {html.escape(game.author)}\n"
                    f"   📦 <i>Размер:</i> {html.escape(game.size)}\n"
                    f"   📅 <i>Дата добавления:</i> {date_display}\n"
                    f"   🔗 <a href='{game.url}'>Ссылка</a>\n\n"
                )
            
            await message.answer(response, parse_mode='HTML', disable_web_page_preview=True)
        except Exception as e:
            logger.error(f"Ошибка при получении последних игр: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await message.answer(f"❌ Ошибка: {e}")

# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "ℹ️ <b>Справка по командам:</b>\n\n"
        "/start - Запуск бота\n"
        "/status - Статус работы бота\n"
        "/check_now - Проверить новые игры сейчас\n"
        "/stats - Статистика базы данных\n"
        "/last - Показать последние игры\n"
        "/help - Эта справка\n\n"
        f"<i>Бот автоматически проверяет RuTracker каждые {config.CHECK_INTERVAL//60} минут "
        "и отправляет уведомления о новых играх.</i>"
    )
    
    await message.answer(help_text, parse_mode='HTML')

async def check_new_games():
    """Проверка новых игр"""
    try:
        logger.info("Начинаю проверку новых игр...")
        
        new_games = await parser.get_new_games()
        
        if not new_games:
            logger.info("Новых игр не найдено.")
            # ЗАКОММЕНТИРОВАНО: Отправка сообщения о пустой проверке
            # await bot.send_message(
            #     config.ADMIN_ID,
            #     "ℹ️ Проверка завершена. Новых игр не найдено."
            # )
            return
        
        logger.info(f"Найдено {len(new_games)} новых игр.")
        
        successful_notifications = 0
        
        for game_data in new_games:
            try:
                async with async_session() as session:
                    # Проверяем, есть ли уже такая игра в базе
                    existing = await session.execute(
                        text("SELECT id FROM games WHERE topic_id = :topic_id"),
                        {"topic_id": game_data['topic_id']}
                    )
                    
                    if existing.scalar_one_or_none():
                        logger.info(f"Игра {game_data['topic_id']} уже есть в базе, пропускаем")
                        continue
                    
                    # Исправляем получение описания
                    description = game_data.get('description')
                    if description is None:
                        description = ''
                    
                    # Сохраняем игру в базу
                    game = Game(
                        topic_id=game_data['topic_id'],
                        title=game_data['title'],
                        url=game_data['url'],
                        author=game_data.get('author', 'Неизвестно'),
                        size=game_data.get('size', 'N/A'),
                        seeds=game_data.get('seeds', 0),
                        leeches=game_data.get('leeches', 0),
                        replies=game_data.get('replies', 0),
                        downloads=game_data.get('downloads', 0),
                        last_post_date=game_data.get('last_post_date'),
                        genre=game_data.get('genre'),
                        languages=game_data.get('languages'),
                        version=game_data.get('version'),
                        description=description[:500]
                    )
                    
                    session.add(game)
                    await session.commit()
                    
                    # Получаем ID игры для обновления
                    result = await session.execute(
                        text("SELECT id FROM games WHERE topic_id = :topic_id"),
                        {"topic_id": game_data['topic_id']}
                    )
                    game_id = result.scalar_one()
                    
                    # Отправляем уведомление
                    await send_notification(game)
                    
                    # Отмечаем как уведомленную
                    await session.execute(
                        text("UPDATE games SET is_notified = 1 WHERE id = :game_id"),
                        {"game_id": game_id}
                    )
                    await session.commit()
                    
                    successful_notifications += 1
                    logger.info(f"✅ Уведомление отправлено для игры: {game.title}")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка при обработке игры {game_data.get('topic_id')}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        # Обновляем время последней проверки
        async with async_session() as session:
            await session.execute(
                text("UPDATE settings SET value = datetime('now'), updated_at = datetime('now') "
                     "WHERE key = 'last_check'")
            )
            await session.commit()
        
        logger.info(f"✅ Успешно обработано {successful_notifications} новых игр.")
        
        # Отправляем итоговое сообщение
        if successful_notifications > 0:
            await bot.send_message(
                config.ADMIN_ID,
                f"✅ <b>Проверка завершена!</b> Найдено и отправлено <b>{successful_notifications}</b> новых игр.",
                parse_mode='HTML'
            )
            
    except Exception as e:
        logger.error(f"Ошибка при проверке новых игр: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Отправляем уведомление об ошибке администратору
        try:
            await bot.send_message(
                config.ADMIN_ID,
                f"⚠️ <b>Ошибка при проверке RuTracker:</b>\n<code>{html.escape(str(e)[:1000])}</code>",
                parse_mode='HTML'
            )
        except Exception as send_err:
            logger.error(f"Не удалось отправить уведомление об ошибке: {send_err}")

async def send_notification(game: Game):
    """Отправка уведомления о новой игре"""
    try:
        # Форматируем сообщение КАК В СТАРОМ ВАРИАНТЕ
        message = (
            f"🎮 <b>НОВАЯ ИГРА НА RUTRACKER!</b>\n\n"
            f"<b>{html.escape(game.title)}</b>\n\n"
        )
        
        if game.genre:
            message += f"🎭 <b>Жанр:</b> {html.escape(game.genre)}\n"
        
        if game.languages:
            message += f"🌐 <b>Языки:</b> {html.escape(game.languages)}\n"
        
        if game.version:
            message += f"🔢 <b>Версия:</b> {html.escape(game.version)}\n"
        
        message += (
            f"👤 <b>Автор:</b> {html.escape(game.author)}\n"
            f"📦 <b>Размер:</b> {html.escape(game.size)}\n"
            f"⬆️ <b>Сиды:</b> {game.seeds} | ⬇️ <b>Личи:</b> {game.leeches}\n"
            f"💬 <b>Ответов:</b> {game.replies} | 📥 <b>Скачиваний:</b> {game.downloads}\n\n"
        )
        
        if game.description:
            message += f"📝 <b>Описание:</b>\n{html.escape(game.description[:300])}...\n\n"
        
        message += f"🔗 <a href='{game.url}'>Ссылка на раздачу</a>"
        
        # Отправляем сообщение с ВКЛЮЧЕННЫМ предпросмотром
        await bot.send_message(
            chat_id=config.ADMIN_ID,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=False  # ВКЛЮЧЕНО - предпросмотр будет
        )
        
        logger.info(f"Отправлено уведомление о игре: {game.title}")
        
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления: {e}")
        import traceback
        logger.error(traceback.format_exc())

async def on_startup():
    """Действия при запуске бота"""
    logger.info("Бот запускается...")
    
    try:
        # Инициализация базы данных
        await init_db()
        logger.info("База данных инициализирована")
        
        # Запуск планировщика
        scheduler.add_job(
            check_new_games,
            trigger=IntervalTrigger(seconds=config.CHECK_INTERVAL),
            id='check_new_games',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info(f"Планировщик запущен. Интервал: {config.CHECK_INTERVAL} секунд")
        
        # Отправляем сообщение о запуске (если нужно)
        try:
            await bot.send_message(
                config.ADMIN_ID,
                "🤖 <b>Бот запущен и начал отслеживание новых игр на RuTracker!</b>\n"
                "Используйте /help для просмотра команд.",
                parse_mode='HTML'
            )
        except:
            pass  # Если не получится отправить - не страшно
        
        logger.info("Бот готов к работе. Отправьте /start в Telegram")
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

async def on_shutdown():
    """Действия при остановке бота"""
    logger.info("Бот останавливается...")
    
    try:
        # Останавливаем планировщик
        if scheduler.running:
            scheduler.shutdown()
        
        # Закрываем сессию бота
        await bot.session.close()
        
        logger.info("Бот остановлен")
        
    except Exception as e:
        logger.error(f"Ошибка при остановке бота: {e}")

async def main():
    """Основная функция"""
    try:
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Запуск бота
        logger.info("Запускаю polling...")
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logger.error(f"Критическая ошибка в main: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    asyncio.run(main())
