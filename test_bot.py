#!/usr/bin/env python3
"""
Test script for RuTracker Telegram Bot
Tests Telegram API connectivity and bot configuration
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Добавляем путь для импорта модулей бота
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

async def test_bot():
    """Test Telegram bot connection"""
    from aiogram import Bot
    
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_ID = os.getenv('ADMIN_ID')
    
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN не найден в .env файле")
        return
    
    if not ADMIN_ID:
        print("❌ ADMIN_ID не найден в .env файле")
        return
    
    bot = Bot(token=BOT_TOKEN)
    
    try:
        # Test bot connection
        me = await bot.get_me()
        print(f"✅ Бот подключен: @{me.username} ({me.full_name})")
        print(f"🆔 ID бота: {me.id}")
        
        # Test sending message
        try:
            await bot.send_message(
                chat_id=int(ADMIN_ID),
                text="🤖 Тестовое сообщение от RuTracker Bot\n"
                     "Бот работает корректно!"
            )
            print(f"✅ Сообщение отправлено пользователю {ADMIN_ID}")
            
        except Exception as e:
            print(f"⚠️ Не удалось отправить сообщение: {e}")
            print("\n🔍 Возможные причины:")
            print("1. Пользователь с ID {ADMIN_ID} не начинал диалог с ботом")
            print("2. Пользователь заблокировал бота")
            print("3. Неверный ID пользователя")
            
    except Exception as e:
        print(f"❌ Ошибка подключения к Telegram API: {e}")
        print(f"🔑 Проверьте токен: {BOT_TOKEN[:10]}...")
        
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_bot())
