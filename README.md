# Chat Application with OpenAI Integration

## Требования
- Python 3.11+
- MySQL 8.0+
- Redis
- FFmpeg

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/rorekhov-proger/korgan_20250526.git
cd korgan_20250526
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env в корневой директории проекта:
```
# Основные настройки Flask
SECRET_KEY=your-secret-key
FLASK_ENV=development  # development или production
FLASK_HOST=0.0.0.0    # По умолчанию 0.0.0.0
FLASK_PORT=5000       # По умолчанию 5000

# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_BASE_URL=https://api.openai.com/v1

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DB=korgan_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

5. Настройте базу данных:
```bash
# Создайте базу данных
mysql -u root -p
CREATE DATABASE korgan_db;
exit;

# Примените миграции
flask db upgrade
```

6. Установите FFmpeg:
- Windows: Скачайте [ffmpeg-git-full.7z](https://www.gyan.dev/ffmpeg/builds/) и распакуйте в C:\ffmpeg
- Linux: `sudo apt-get install ffmpeg`
- Mac: `brew install ffmpeg`

## Запуск

1. Убедитесь, что Redis запущен
2. Запустите приложение:
```bash
python run.py
```

Приложение будет доступно по адресу, указанному в настройках (по умолчанию: http://localhost:5000)

## Режимы работы

### Разработка (development)
- Включен режим отладки
- Подробные сообщения об ошибках
- Автоматическая перезагрузка при изменении кода

### Продакшен (production)
- Отключен режим отладки
- Минимальные сообщения об ошибках
- Оптимизированная производительность

## Функциональность
- Аутентификация пользователей
- Создание и управление чатами
- Интеграция с OpenAI GPT
- Загрузка и обработка аудио файлов
- Контекстное меню для управления чатами
- Поддержка различных моделей GPT