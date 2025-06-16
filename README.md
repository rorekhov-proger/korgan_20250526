# Chat Application with OpenAI Integration

## Описание
Многофункциональный чат-ассистент с поддержкой протоколов, поручений, распознавания аудио, автозаполнения форм через ИИ (OpenAI GPT), современным UI/UX и интеграцией с MySQL, Redis, FFmpeg.

### Основные возможности
- Аутентификация пользователей (регистрация, вход, сессии)
- Современный дизайн форм и бокового меню (адаптивно, с иконками, градиентами)
- Список чатов
- Загрузка и распознавание аудио (FFmpeg + OpenAI)
- Автоматическое извлечение данных для протоколов и поручений из текста/аудио
- Генерация Markdown-протоколов (режимы: полное/быстрое заполнение)
- Модальное окно для редактирования протокола с автозаполнением через ИИ
- Flash-уведомления с анимацией и цветовой дифференциацией
- Контекстное меню для управления чатами
- Поддержка различных моделей GPT

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
4. Создайте файл .env в корне проекта и заполните переменные (см. пример ниже):
```
SECRET_KEY=your-secret-key
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_BASE_URL=https://api.openai.com/v1
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DB=korgan_db
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```
5. Настройте базу данных:
```bash
mysql -u root -p
CREATE DATABASE korgan_db;
```
6. Примените миграции:
```bash
flask db upgrade
```
7. Установите FFmpeg:
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
- **Разработка (development):** отладка, подробные ошибки, авто-ребут
- **Продакшен (production):** оптимизация, минимум ошибок

## Функциональность
- Аутентификация и регистрация
- Современный UI/UX (градиенты, иконки, анимации, адаптивность)
- Список чатов, контекстное меню
- Загрузка и распознавание аудио, автозаполнение протоколов
- Генерация и редактирование протоколов (Markdown)
- Flash-уведомления, модальные окна, кнопки с иконками
- Интеграция с OpenAI GPT, поддержка разных моделей
- Работа с MySQL, Redis, FFmpeg

## Структура проекта
- `app/` — основной код Flask-приложения (модели, сервисы, роуты, формы)
- `app/static/` — CSS, JS, загружаемые файлы
- `app/templates/` — Jinja2-шаблоны
- `scripts/` — вспомогательные скрипты (тесты, сброс БД и т.д.)