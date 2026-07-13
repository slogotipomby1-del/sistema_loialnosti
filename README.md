# Система лояльности «Корпоративный стиль»

Готовый MVP реферальной системы и системы лояльности с Telegram-ботом и закрытой Django-админкой.

## Что уже работает

- Telegram-бот для участников программы
- регистрация участника и создание персональной ссылки
- заявки по рефералам
- собственные заявки участника
- каталог подарков за бонусы
- запросы на списание бонусов
- уведомления администратору в Telegram
- закрытая админка для ручной обработки заявок и бонусов

## Как устроен MVP

### Для участника

- регистрируется в Telegram-боте
- получает персональную ссылку
- приглашает клиентов
- видит баланс бонусов
- отправляет собственные заявки
- запрашивает подарки или списание бонусов

### Для администратора

- открывает админку в браузере
- видит новые заявки и запросы на списание
- вручную проверяет кейсы
- меняет статусы
- вручную подтверждает бонусы

## Структура проекта

- `backend/` — Django-проект, модели, админка, бот, тесты
- `deploy/systemd/` — готовые unit-файлы для сервера
- `deploy/nginx/` — конфиг nginx для админки
- `docs/` — проектные и deployment-документы

## Локальный запуск

### 1. Установка

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev,prod]
```

### 2. Переменные окружения

Скопируйте шаблон:

```bash
copy ..\.env.example ..\.env
```

И заполните реальные значения.

### 3. База и админка

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py runserver
```

Админка:

- `http://127.0.0.1:8000/admin/`
- `http://127.0.0.1:8000/health/` — проверка, что приложение отвечает

### 4. Запуск бота

```bash
python -m apps.bot.run_polling
```

## Полезные команды

Тесты:

```bash
python -m pytest
```

Точечные тесты админки:

```bash
python -m pytest tests/test_admin_panel.py tests/test_admin_change_memo.py tests/test_admin_index.py tests/test_admin_notifications.py
```

## Продакшн на сервере

На сервере используются:

- `gunicorn` для Django-админки
- `systemd` для админки и бота
- `nginx` как внешний вход в админку

Основные файлы:

- `deploy/systemd/referral_admin.service`
- `deploy/systemd/referral_bot.service`
- `deploy/nginx/referral_admin.conf`

Краткий сценарий выкладки:

```bash
cd /opt/sistema_loialnosti
git pull
cd backend
source .venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart referral_admin
systemctl restart referral_bot
systemctl restart nginx
```

Админка на текущем этапе открывается по адресу:

- `http://142.93.49.181/admin/`
- `http://142.93.49.181/health/`

## Что важно помнить

- amoCRM пока не подключён — это этап 2
- начисление и списание бонусов в MVP подтверждаются вручную
- Telegram-бот и админка уже покрыты базовыми тестами
