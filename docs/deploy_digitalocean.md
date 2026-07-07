# Деплой на DigitalOcean

Ниже базовый путь запуска MVP на сервере Ubuntu в DigitalOcean.

## 1. Что должно быть на сервере

- Python 3.12
- PostgreSQL
- Nginx
- systemd
- git

## 2. Что нужно подготовить

- домен или поддомен для админки
- Telegram bot token
- Telegram chat id администратора
- строку подключения `DATABASE_URL`
- `DJANGO_SECRET_KEY`

## 3. Переменные окружения

Пример production-набора:

```env
DJANGO_SECRET_KEY=very-secret-key
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=admin.example.com,server_ip
DJANGO_CSRF_TRUSTED_ORIGINS=https://admin.example.com
DATABASE_URL=postgres://user:password@127.0.0.1:5432/referral_mvp
TELEGRAM_BOT_TOKEN=telegram-token
TELEGRAM_ADMIN_CHAT_ID=123456789
```

## 4. Установка проекта

```bash
git clone https://github.com/slogotipomby1-del/sistema_loialnosti.git
cd sistema_loialnosti/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .[dev,prod]
```

## 5. Подготовка Django

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 6. Запуск админки через gunicorn

Пример команды:

```bash
gunicorn config.wsgi:application --bind 127.0.0.1:8000
```

## 7. Дальше подключается Nginx

Nginx должен:

- отдавать `staticfiles`
- проксировать админку на `127.0.0.1:8000`
- принимать HTTPS

## 8. Что делать следующим этапом

После этого нужно отдельно:

- подключить постоянный запуск Telegram-бота
- вынести секреты в systemd environment file
- настроить SSL
- сделать backup PostgreSQL
