# Chat Application with OpenAI Integration

## Описание
Многофункциональный чат-ассистент с поддержкой протоколов, поручений, распознавания аудио, автозаполнения форм через ИИ (OpenAI GPT), современным UI/UX и интеграцией с MySQL, Redis, FFmpeg.

### Основные возможности
- Аутентификация пользователей (регистрация, вход, сессии)
- Современный дизайн форм и бокового меню (адаптивно, с иконками, градиентами)
- Список чатов, контекстное меню
- Загрузка и распознавание аудио (FFmpeg + OpenAI Whisper)
- Автоматическое извлечение данных для протоколов и поручений из текста/аудио
- Генерация Markdown-протоколов (режимы: полное/быстрое заполнение)
- Модальное окно для редактирования протокола с автозаполнением через ИИ
- Flash-уведомления с анимацией и цветовой дифференциацией
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

# ASR backend (speech to text)
# whisper | faster-whisper | ollama
ASR_BACKEND=ollama
# Optional for Ollama:
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_ASR_MODEL=whisper
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

## Структура проекта
- `app/` — основной код Flask-приложения (модели, сервисы, роуты, формы, утилиты)
- `app/static/` — CSS, JS, загружаемые файлы
- `app/templates/` — Jinja2-шаблоны
- `scripts/` — вспомогательные миграции и тесты (только актуальные)

## Примечания
- Для работы с Whisper требуется поддержка CUDA (GPU) для ускорения распознавания аудио.
- Все основные настройки и ключи задаются через .env.

## Ollama: локальные модели

- Чат‑модели (рекомендуемые теги):
	- `llama3.1:8b` — стабильный общий ассистент (англ. контент, следование инструкциям)
	- `qwen2.5:7b-instruct` — сильнее в мультиязычности (русский), код/рассуждения

Короткая рекомендация:
- Нужен русский/код — берите `qwen2.5:7b-instruct`
- Нужен общий ассистент (англ) — `llama3.1:8b`

Установка моделей:
```powershell
ollama pull llama3.1:8b
ollama pull qwen2.5:7b-instruct
```

Проверка установленных моделей:
```powershell
Invoke-RestMethod http://localhost:11434/api/tags | ConvertTo-Json -Depth 6
```

## ASR (распознавание речи)

- Поддерживаются два бэкенда:
	- `whisper` (локальная библиотека `openai-whisper`)
	- `ollama` (если установлен подходящий аудио‑модельный тег)

Переключение бэкенда в `.env`:
```env
ASR_BACKEND=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_ASR_MODEL=whisper:small
```

Важно: если указанная в Ollama аудио‑модель не установлена, приложение автоматически выполнит фолбэк на локальный Whisper. Для Whisper убедитесь, что в системе установлен `ffmpeg`, и зависимости из `requirements.txt` установлены.

## Быстрый тест Ollama из PowerShell

```powershell
$body = '{"model":"llama3.1:8b","messages":[{"role":"user","content":"Привет!"}],"stream":false}';
Invoke-RestMethod -Method Post -Uri http://localhost:11434/api/chat -Body $body -ContentType 'application/json' | ConvertTo-Json -Depth 5
```