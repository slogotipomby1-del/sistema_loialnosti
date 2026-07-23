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
- главный экран админки с быстрыми переходами и сводкой по очереди работы
- ручные корректировки, аннулирование бонусов и поддержка отрицательного баланса
- автоматические предупреждения о скором сгорании бонусов и автоматическое сгорание остатка

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
- при необходимости назначает основной контакт компании
- видит быстрые действия, дубли, баланс и историю операций прямо в админке

## Структура проекта

- `backend/` — Django-проект, модели, админка, бот, тесты
- `deploy/systemd/` — готовые unit-файлы для сервера
- `deploy/nginx/` — конфиг nginx для админки
- `docs/` — проектные и deployment-документы

## Полезные документы

- `docs/2026-07-15_Регламент_администратора_MVP.md` — как администратору работать с заявками, бонусами и спорными случаями
- `docs/2026-07-15_Короткий_итог_MVP.md` — что уже готово в MVP, как этим пользоваться и что остаётся на этап 2
- `docs/2026-07-20_Чек-лист_приемки_MVP.md` — быстрый список проверки перед запуском и после обновлений
- `docs/deploy_digitalocean.md` — как развернуть и обновлять проект на сервере

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
- `systemd timer` для предупреждений о сгорании бонусов и ежедневного сгорания остатка

Основные файлы:

- `deploy/systemd/referral_admin.service`
- `deploy/systemd/referral_bot.service`
- `deploy/systemd/bonus_expiration_warning.service`
- `deploy/systemd/bonus_expiration_warning.timer`
- `deploy/systemd/bonus_expiration.service`
- `deploy/systemd/bonus_expiration.timer`
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

```bash
cd /opt/sistema_loialnosti/backend
source .venv/bin/activate
python manage.py send_bonus_expiration_warnings --dry-run
python manage.py expire_bonus_entries --dry-run
```

Админка на текущем этапе открывается по адресу:

- `http://142.93.49.181/admin/`
- `http://142.93.49.181/health/`

## Что важно помнить

- amoCRM пока не подключён — это этап 2
- начисление и списание бонусов в MVP подтверждаются вручную
- после аннулирования подтверждённого бонуса баланс участника может стать отрицательным — это нормальный рабочий сценарий
- предупреждение о скором сгорании бонусов и само сгорание настроены как отдельные серверные задачи
- Telegram-бот и админка уже покрыты базовыми тестами
