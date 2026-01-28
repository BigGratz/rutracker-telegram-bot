# 📦 RuTracker Telegram Bot

![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)

---

🎮 **О проекте**
------------

**RuTracker Telegram Bot** — это мощный автоматический бот для отслеживания новых игр в разделе "Горячие Новинки" (f=635) на RuTracker.org. Бот парсит форум каждые 5 минут, находит новые раздачи и отправляет подробные уведомления в Telegram.

✨ Возможности
-------------

✅ Автоматический парсинг RuTracker каждые 5 минут

✅ Умные уведомления в Telegram с полной информацией

✅ База данных SQLite для хранения истории

✅ 6 команд управления через Telegram

✅ Systemd сервис для автозапуска

✅ Резервное копирование базы данных

✅ Мониторинг здоровья системы

✅ Поддержка прокси (опционально)

✅ Подробное логирование

📋 Содержание
-------------

*   [🚀 Быстрый старт](#quick-start)
*   [⚙️ Установка](#installation)
*   [🔧 Конфигурация](#configuration)
*   [🤖 Команды бота](#commands)
*   [🛠️ Развертывание на VPS](#deployment)
*   [📦 Systemd сервис](#systemd)
*   [💾 Резервное копирование](#backup)
*   [🐛 Решение проблем](#troubleshooting)
*   [🔍 FAQ](#faq)
*   [📄 Лицензия](#license)

🚀 Быстрый старт
----------------

### Минимальные требования

*   Python 3.12+
*   Ubuntu 22.04+ / Debian 11+ / CentOS 8+
*   512MB RAM, 10GB SSD
*   Аккаунт Telegram

### Установка за 5 минут

    # 1. Клонируйте репозиторий
    git clone https://github.com/BigGratz/rutracker-telegram-bot.git
    cd rutracker-telegram-bot
    
    # 2. Настройте окружение
    cp .env.example .env
    nano .env  # Отредактируйте конфигурацию
    
    # 3. Установите зависимости
    python3.12 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # 4. Протестируйте бота
    python test_bot.py
    
    # 5. Запустите бота
    python run_bot.py

⚙️ Установка
------------

### Подробная установка на Ubuntu 24.04

    # Обновите систему
    sudo apt update && sudo apt upgrade -y
    
    # Установите Python и инструменты
    sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip \
        git curl wget sqlite3 tree htop
    
    # Создайте пользователя для бота (рекомендуется)
    sudo useradd -m -s /bin/bash rutrackerbot
    sudo passwd rutrackerbot
    su - rutrackerbot
    
    # Клонируйте проект
    git clone https://github.com/BigGratz/rutracker-telegram-bot.git
    cd rutracker-telegram-bot
    
    # Настройте виртуальное окружение
    python3.12 -m venv venv
    source venv/bin/activate
    
    # Установите зависимости
    pip install --upgrade pip
    pip install -r requirements.txt

🔧 Конфигурация
---------------

### Файл .env

Создайте файл `.env` на основе примера:

    cp .env.example .env
    nano .env

### Обязательные настройки:

    # Telegram Bot Configuration
    BOT_TOKEN=Ваш Токен  # Получите у @BotFather
    ADMIN_ID=Ваш ID                                         # Ваш Telegram ID
    
    # RuTracker Configuration
    RUTRACKER_URL=https://rutracker.org/forum/viewforum.php?f=635
    CHECK_INTERVAL=300  # Интервал проверки в секундах (5 минут)

### Опциональные настройки:

    # Прокси конфигурация (если нужен)
    USE_PROXY=false
    PROXY_URL=http://proxy:port
    PROXY_USER=username
    PROXY_PASSWORD=password
    
    # User-Agent для парсинга
    USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36

**Как получить BOT\_TOKEN:**  
1\. Откройте Telegram  
2\. Найдите `@BotFather`  
3\. Отправьте `/newbot`  
4\. Следуйте инструкциям  
5\. Скопируйте токен в `BOT_TOKEN`

**Как получить ADMIN\_ID:**  
1\. Откройте Telegram  
2\. Найдите `@userinfobot`  
3\. Отправьте любое сообщение  
4\. Скопируйте ваш ID в `ADMIN_ID`

🤖 Команды бота
---------------

### Основные команды

Команда

Описание

Пример

`/start`

Запуск бота и приветствие

`/start`

`/status`

Статус работы бота

`/status`

`/check_now`

Принудительная проверка

`/check_now`

`/stats`

Статистика базы данных

`/stats`

`/last`

Последние 5 игр

`/last`

`/help`

Справка по командам

`/help`

### Пример ответа на команду `/status`

    🤖 Статус бота: Работает
    📊 Запланированные задачи: 1
    ⏰ Интервал проверки: 300 секунд
    🔍 Автопроверка: активна
    🎯 Отслеживаемый раздел:
    https://rutracker.org/forum/viewforum.php?f=635

### Пример уведомления о новой игре

    🎮 НОВАЯ ИГРА НА RUTRACKER!
    
    [DL] Earth Must Die [P] [ENG + 3 / ENG] (2026, Adventure) (1.8882) [Portable]
    
    👤 Автор: LinguaLatina
    📦 Размер: 1.79 GB
    ⬆️ Сиды: 39 | ⬇️ Личи: 4
    💬 Ответов: 0 | 📥 Скачиваний: 128
    
    🔗 Ссылка на раздачу

🛠️ Развертывание на VPS
------------------------

### Полная установка на чистый сервер

    #!/bin/bash
    # save_as: deploy_bot.sh
    
    # 1. Настройка системы
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y python3.12 python3.12-venv git curl sqlite3
    
    # 2. Создание пользователя
    sudo useradd -m -s /bin/bash rutrackerbot
    sudo passwd rutrackerbot
    sudo usermod -aG sudo rutrackerbot
    
    # 3. Клонирование проекта
    su - rutrackerbot
    git clone https://github.com/BigGratz/rutracker-telegram-bot.git
    cd rutracker-telegram-bot
    
    # 4. Настройка окружения
    python3.12 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # 5. Конфигурация
    cp .env.example .env
    echo "Отредактируйте файл .env: nano .env"
    echo "Добавьте BOT_TOKEN и ADMIN_ID"
    read -p "Нажмите Enter после редактирования..."
    
    # 6. Тестирование
    python test_bot.py

### Проверка работы

    # Запуск вручную для тестирования
    source venv/bin/activate
    python run_bot.py
    
    # В отдельной сессии проверьте логи
    tail -f bot.log

📦 Systemd сервис
-----------------

### Создание сервиса

    # Создайте файл сервиса
    sudo nano /etc/systemd/system/rutracker-bot.service

### Конфигурация сервиса

    [Unit]
    Description=Rutracker Telegram Bot
    After=network.target
    Wants=network.target
    
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
    ProtectSystem=strict
    PrivateTmp=true
    PrivateDevices=true
    ProtectHome=true
    ReadWritePaths=/home/rutrackerbot/rutracker-telegram-bot
    
    [Install]
    WantedBy=multi-user.target

### Управление сервисом

    # Активация сервиса
    sudo systemctl daemon-reload
    sudo systemctl enable rutracker-bot.service
    sudo systemctl start rutracker-bot.service
    
    # Команды управления
    sudo systemctl status rutracker-bot.service    # Статус
    sudo systemctl stop rutracker-bot.service      # Остановка
    sudo systemctl restart rutracker-bot.service   # Перезапуск
    sudo systemctl disable rutracker-bot.service   # Отключение автозапуска
    
    # Просмотр логов
    sudo journalctl -u rutracker-bot.service -f    # Логи в реальном времени
    sudo journalctl -u rutracker-bot.service -n 50 # Последние 50 строк
    sudo journalctl -u rutracker-bot.service --since "1 hour ago" # За последний час

💾 Резервное копирование
------------------------

### Автоматические бэкапы

    # Создайте скрипт резервного копирования
    nano ~/rutracker-telegram-bot/backup.sh

    #!/bin/bash
    BACKUP_DIR="/home/rutrackerbot/backups"
    DATE=$(date +%Y%m%d_%H%M%S)
    DB_FILE="/home/rutrackerbot/rutracker-telegram-bot/bot.db"
    BACKUP_FILE="$BACKUP_DIR/rutracker_bot_$DATE.db"
    
    mkdir -p $BACKUP_DIR
    cp $DB_FILE $BACKUP_FILE
    gzip $BACKUP_FILE
    
    # Удаляем старые бэкапы (старше 30 дней)
    find $BACKUP_DIR -name "*.db.gz" -mtime +30 -delete
    
    echo "Бэкап создан: ${BACKUP_FILE}.gz"

### Настройка автоматических бэкапов

    # Сделайте скрипт исполняемым
    chmod +x ~/rutracker-telegram-bot/backup.sh
    
    # Добавьте в cron (ежедневно в 2:00)
    (crontab -l 2>/dev/null; echo "0 2 * * * /home/rutrackerbot/rutracker-telegram-bot/backup.sh") | crontab -
    
    # Проверьте настройки cron
    crontab -l

🐛 Решение проблем
------------------

### Распространенные проблемы

1\. Бот не запускается

    # Проверьте логи
    sudo journalctl -u rutracker-bot.service -n 100
    
    # Проверьте зависимости
    source venv/bin/activate
    pip list | grep aiogram
    
    # Проверьте токен
    cat .env | grep BOT_TOKEN

2\. Не приходят уведомления

    # Проверьте последний topic_id
    sqlite3 bot.db "SELECT value FROM settings WHERE key = 'last_topic_id';"
    
    # Принудительно обновите на старое значение
    sqlite3 bot.db "UPDATE settings SET value = '6800000' WHERE key = 'last_topic_id';"
    
    # Перезапустите бота
    sudo systemctl restart rutracker-bot.service

3\. Ошибки парсинга

    # Проверьте доступность RuTracker
    curl -I https://rutracker.org/forum/viewforum.php?f=635
    
    # Проверьте User-Agent
    cat .env | grep USER_AGENT

4\. Ошибка с базой данных

    # Проверьте целостность базы данных
    sqlite3 bot.db "PRAGMA integrity_check;"
    
    # Сделайте резервную копию и пересоздайте
    cp bot.db bot.db.backup
    rm bot.db
    python -c "from bot.database import init_db; import asyncio; asyncio.run(init_db())"

### Полезные команды для отладки

    # Просмотр логов в реальном времени
    tail -f bot.log
    
    # Проверка статуса сервиса
    sudo systemctl status rutracker-bot.service
    
    # Проверка базы данных
    sqlite3 bot.db ".tables"
    sqlite3 bot.db "SELECT COUNT(*) FROM games;"
    sqlite3 bot.db "SELECT * FROM settings;"
    
    # Проверка подключения к Telegram
    source venv/bin/activate
    python test_bot.py

🔍 FAQ
------

❓ Как изменить интервал проверки?

Измените `CHECK_INTERVAL` в файле `.env`. Значение в секундах (300 = 5 минут).

❓ Как добавить нескольких администраторов?

Текущая версия поддерживает одного администратора. Для нескольких нужно изменить код в `bot/main.py`.

❓ Бот не видит новые игры. Что делать?

Проверьте `last_topic_id` в базе данных:

    sqlite3 bot.db "UPDATE settings SET value = '0' WHERE key = 'last_topic_id';"
    sudo systemctl restart rutracker-bot.service

❓ Как изменить отслеживаемый раздел?

Измените `RUTRACKER_URL` в файле `.env`. Например, для f=313 (Игры для Linux):

    RUTRACKER_URL=https://rutracker.org/forum/viewforum.php?f=313

❓ Как настроить прокси?

Раскомментируйте и настройте прокси в файле `.env`:

    USE_PROXY=true
    PROXY_URL=http://your-proxy:port
    PROXY_USER=username
    PROXY_PASSWORD=password

❓ Как обновить бота?

    cd ~/rutracker-telegram-bot
    git pull origin main
    source venv/bin/activate
    pip install -r requirements.txt
    sudo systemctl restart rutracker-bot.service

📄 Лицензия
-----------

Этот проект лицензирован под лицензией MIT. Смотрите файл `LICENSE` для подробностей.

**👥 Вклад в проект**  
Вклады приветствуются! Пожалуйста, прочитайте `CONTRIBUTING.md` для деталей.

**⭐ Поддержка**  
Если вам понравился проект, поставьте звезду на GitHub!

**📞 Контакты**  
• GitHub Issues: [Отчеты об ошибках](https://github.com/BigGratz/rutracker-telegram-bot/issues)  
• Telegram: @BigGratz
