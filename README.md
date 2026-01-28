<p align="center">
  <img src="https://raw.githubusercontent.com/BigGratz/rutracker-telegram-bot/main/assets/banner.png" width="900">
</p>

<h1 align="center">📦 RuTracker Telegram Bot</h1>

<p align="center">
  <b>Автоматический Telegram-бот для отслеживания новых игр на RuTracker</b><br>
  Быстро • Надёжно • Полностью автономно
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/BigGratz/rutracker-telegram-bot?style=for-the-badge">
  <img src="https://img.shields.io/github/license/BigGratz/rutracker-telegram-bot?style=for-the-badge">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram">
</p>

---

## ✨ Особенности

- 🔄 **Автоматический парсинг** каждые 5 минут  
- 🔔 **Умные уведомления** с полной информацией о раздачах  
- 💾 **База данных SQLite** для хранения истории  
- 🤖 **6 команд управления** через Telegram  
- 🛡️ **Systemd сервис** для автозапуска  
- 📊 **Мониторинг здоровья** системы  
- 🔌 **Поддержка прокси** (опционально)  
- 📝 **Подробное логирование**  

---

## 📋 Содержание

- [🚀 Быстрый старт](#быстрый-старт)
- [⚙️ Установка](#установка)
- [🔧 Конфигурация](#конфигурация)
- [🤖 Команды бота](#команды-бота)
- [🛠️ Развертывание на VPS](#развертывание-на-vps)
- [📦 Systemd сервис](#systemd-сервис)
- [💾 Резервное копирование](#резервное-копирование)
- [🐛 Решение проблем](#решение-проблем)
- [❓ FAQ](#faq)
- [📄 Лицензия](#лицензия)

---

<a name="быстрый-старт"></a>
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

---

<a name="установка"></a>
## ⚙️ Установка

Подробная установка на Ubuntu 24.04

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip \
    git curl wget sqlite3

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

---

<a name="конфигурация"></a>
## 🔧 Конфигурация

Создайте файл `.env` на основе `.env.example`:

```env
# ОБЯЗАТЕЛЬНЫЕ НАСТРОЙКИ
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id
RUTRACKER_URL=https://rutracker.org/forum/viewforum.php?f=635
CHECK_INTERVAL=300

# ОПЦИОНАЛЬНЫЕ НАСТРОЙКИ
USE_PROXY=false
PROXY_URL=http://proxy:port
PROXY_USER=username
PROXY_PASSWORD=password
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

---

<a name="команды-бота"></a>
## 🤖 Команды бота

| Команда | Описание | Пример |
|-------|----------|--------|
| /start | Запуск бота и приветствие | /start |
| /status | Статус работы бота | /status |
| /check_now | Принудительная проверка | /check_now |
| /stats | Статистика базы данных | /stats |
| /last | Последние 5 найденных игр | /last |
| /help | Справка по командам | /help |

---

📨 **Пример уведомления**

```
🎮 НОВАЯ ИГРА НА RUTRACKER!

[DL] Earth Must Die [P] [ENG + 3 / ENG] (2026, Adventure) (1.8882) [Portable]

👤 Автор: LinguaLatina
📦 Размер: 1.79 GB
⬆️ Сиды: 39 | ⬇️ Личи: 4
💬 Ответов: 0 | 📥 Скачиваний: 128

🔗 Ссылка на раздачу
```

---

<a name="развертывание-на-vps"></a>
## 🛠️ Развертывание на VPS

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

---

<a name="systemd-сервис"></a>
## 📦 Systemd сервис

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

MemoryLimit=512M
CPUQuota=50%

NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### Активация

```bash
sudo systemctl daemon-reload
sudo systemctl enable rutracker-bot.service
sudo systemctl start rutracker-bot.service
```

### Просмотр логов

```bash
sudo journalctl -u rutracker-bot.service -f
sudo journalctl -u rutracker-bot.service --since "1 hour ago"
```

---

<a name="резервное-копирование"></a>
## 💾 Резервное копирование

```bash
#!/bin/bash
BACKUP_DIR="/home/rutrackerbot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="/home/rutrackerbot/rutracker-telegram-bot/bot.db"
BACKUP_FILE="$BACKUP_DIR/rutracker_bot_$DATE.db"

mkdir -p $BACKUP_DIR
cp $DB_FILE $BACKUP_FILE
gzip $BACKUP_FILE

find $BACKUP_DIR -name "*.db.gz" -mtime +30 -delete
```

---

<a name="решение-проблем"></a>
## 🐛 Решение проблем

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

---

<a name="faq"></a>
## ❓ FAQ

**Как изменить интервал проверки?**  
Измените `CHECK_INTERVAL` в файле `.env`.

**Как добавить нескольких администраторов?**  
Требуется изменить код в `bot/main.py`.

**Бот не видит новые игры?**
```bash
sqlite3 bot.db "UPDATE settings SET value = '0' WHERE key = 'last_topic_id';"
sudo systemctl restart rutracker-bot.service
```

**Как изменить отслеживаемый раздел?**
```env
RUTRACKER_URL=https://rutracker.org/forum/viewforum.php?f=313
```

**Как обновить бота?**
```bash
cd ~/rutracker-telegram-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart rutracker-bot.service
```

---

<a name="лицензия"></a>
## 📄 Лицензия

Этот проект распространяется под лицензией MIT.

---

👥 **Вклад в проект**  
Вклады приветствуются! Пожалуйста, создавайте issue или pull request.

⭐ **Поддержка**  
Если проект был полезен — поставьте звезду ⭐

---

Автор: **BigGratz**  
Telegram: @BigGratz  
GitHub: https://github.com/BigGratz
