# 📦 RuTracker Telegram Bot

[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue)](https://t.me)

Автоматический Telegram-бот для отслеживания новых игр в разделе "Горячие Новинки" на RuTracker.org.

## ✨ Особенности

- 🔄 **Автоматический парсинг** каждые 5 минут
- 🔔 **Умные уведомления** с полной информацией о раздачах
- 💾 **База данных SQLite** для хранения истории
- 🤖 **6 команд управления** через Telegram
- 🛡️ **Systemd сервис** для автозапуска
- 📊 **Мониторинг здоровья** системы
- 🔌 **Поддержка прокси** (опционально)
- 📝 **Подробное логирование**

## 📋 Содержание

- [Быстрый старт](#быстрый-старт)
- [Установка](#установка)
- [Конфигурация](#конфигурация)
- [Команды бота](#команды-бота)
- [Развертывание на VPS](#развертывание-на-vps)
- [Systemd сервис](#systemd-сервис)
- [Резервное копирование](#резервное-копирование)
- [Решение проблем](#решение-проблем)
- [FAQ](#faq)
- [Лицензия](#лицензия)

## 🚀 Быстрый старт

### Минимальные требования
- **Python** 3.12+
- **ОС**: Ubuntu 22.04+, Debian 11+, CentOS 8+
- **Память**: 512MB RAM, 10GB SSD
- **Telegram** аккаунт

### Установка за 5 минут
```bash
git clone https://github.com/BigGratz/rutracker-telegram-bot.git
cd rutracker-telegram-bot
cp .env.example .env
nano .env  # Настройте конфигурацию

python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python test_bot.py  # Тестирование
python run_bot.py   # Запуск
```

⚙️ Установка
Подробная установка на Ubuntu 24.04

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip     git curl wget sqlite3

# Создание пользователя (рекомендуется)
sudo useradd -m -s /bin/bash rutrackerbot
sudo passwd rutrackerbot
su - rutrackerbot

# Клонирование и настройка
git clone https://github.com/BigGratz/rutracker-telegram-bot.git
cd rutracker-telegram-bot
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

🔧 Конфигурация

Создайте файл .env на основе .env.example:

```env
# ОБЯЗАТЕЛЬНЫЕ НАСТРОЙКИ
BOT_TOKEN=your_bot_token_here      # Получить у @BotFather
ADMIN_ID=your_telegram_id          # Получить у @userinfobot
RUTRACKER_URL=https://rutracker.org/forum/viewforum.php?f=635
CHECK_INTERVAL=300                  # 5 минут в секундах

# ОПЦИОНАЛЬНЫЕ НАСТРОЙКИ
USE_PROXY=false
PROXY_URL=http://proxy:port
PROXY_USER=username
PROXY_PASSWORD=password
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

🤖 Команды бота

Команда | Описание | Пример
--- | --- | ---
/start | Запуск бота и приветствие | /start
/status | Статус работы бота | /status
/check_now | Принудительная проверка | /check_now
/stats | Статистика базы данных | /stats
/last | Последние 5 найденных игр | /last
/help | Справка по командам | /help

📨 Пример уведомления

```
🎮 НОВАЯ ИГРА НА RUTRACKER!

[DL] Earth Must Die [P] [ENG + 3 / ENG] (2026, Adventure) (1.8882) [Portable]

👤 Автор: LinguaLatina
📦 Размер: 1.79 GB
⬆️ Сиды: 39 | ⬇️ Личи: 4
💬 Ответов: 0 | 📥 Скачиваний: 128

🔗 Ссылка на раздачу
```

🛠️ Развертывание на VPS

Скрипт полной установки deploy_bot.sh:

```bash
#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.12 python3.12-venv git curl sqlite3
sudo useradd -m -s /bin/bash rutrackerbot
sudo passwd rutrackerbot

su - rutrackerbot
git clone https://github.com/BigGratz/rutracker-telegram-bot.git
cd rutracker-telegram-bot
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env файл
python test_bot.py
```

📦 Systemd сервис

Создайте файл /etc/systemd/system/rutracker-bot.service:

```ini
[Unit]
Description=Rutracker Telegram Bot
After=network.target

[Service]
Type=simple
User=rutrackerbot
Group=rutrackerbot
WorkingDirectory=/home/rutrackerbot/rutracker-telegram-bot
Environment="PATH=/home/rutrackerbot/rutracker-telegram-bot/venv/bin"
ExecStart=/home/rutrackerbot/rutracker-telegram-bot/venv/bin/python /home/rutrackerbot/rutracker-telegram-bot/run_bot.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=rutracker-bot

# Ограничения ресурсов
MemoryLimit=512M
CPUQuota=50%

# Безопасность
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

# Активация
```bash
sudo systemctl daemon-reload
sudo systemctl enable rutracker-bot.service
sudo systemctl start rutracker-bot.service
```

# Просмотр логов
```bash
sudo journalctl -u rutracker-bot.service -f
sudo journalctl -u rutracker-bot.service --since "1 hour ago"
```

💾 Резервное копирование

```bash
#!/bin/bash
BACKUP_DIR="/home/rutrackerbot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="/home/rutrackerbot/rutracker-telegram-bot/bot.db"
BACKUP_FILE="$BACKUP_DIR/rutracker_bot_$DATE.db"

mkdir -p $BACKUP_DIR
cp $DB_FILE $BACKUP_FILE
gzip $BACKUP_FILE

# Удаление старых бэкапов (>30 дней)
find $BACKUP_DIR -name "*.db.gz" -mtime +30 -delete
```

Добавьте в cron:

```bash
0 2 * * * /home/rutrackerbot/rutracker-telegram-bot/backup.sh
```

🐛 Решение проблем

### Бот не запускается
```bash
sudo journalctl -u rutracker-bot.service -n 100
cat .env | grep BOT_TOKEN
```

### Не приходят уведомления
```bash
sqlite3 bot.db "SELECT value FROM settings WHERE key = 'last_topic_id';"
sqlite3 bot.db "UPDATE settings SET value = '0' WHERE key = 'last_topic_id';"
sudo systemctl restart rutracker-bot.service
```

### Ошибки парсинга
```bash
curl -I https://rutracker.org/forum/viewforum.php?f=635
cat .env | grep USER_AGENT
```

### Ошибки базы данных
```bash
sqlite3 bot.db "PRAGMA integrity_check;"
cp bot.db bot.db.backup
rm bot.db
python -c "from bot.database import init_db; import asyncio; asyncio.run(init_db())"
```

🔍 FAQ

❓ Как изменить интервал проверки?

Измените CHECK_INTERVAL в файле .env.

❓ Как добавить нескольких администраторов?

Требуется изменить код в bot/main.py.

❓ Бот не видит новые игры?
```bash
sqlite3 bot.db "UPDATE settings SET value = '0' WHERE key = 'last_topic_id';"
sudo systemctl restart rutracker-bot.service
```

❓ Как изменить отслеживаемый раздел?

```env
RUTRACKER_URL=https://rutracker.org/forum/viewforum.php?f=313
```

❓ Как обновить бота?
```bash
cd ~/rutracker-telegram-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart rutracker-bot.service
```

📄 Лицензия

Этот проект распространяется под лицензией MIT.

👥 Вклад в проект

Вклады приветствуются! Пожалуйста, создавайте issue или pull request.

⭐ Поддержка

Если проект был полезен, поставьте звезду на GitHub!

Автор: BigGratz  
Telegram: @BigGratz  
GitHub: https://github.com/BigGratz
