# Деплой на DigitalOcean

Ниже базовый рабочий сценарий запуска MVP на Ubuntu-сервере.

## Что должно быть на сервере

- Python 3.12
- PostgreSQL
- Nginx
- systemd
- git

## Что нужно подготовить

- сервер DigitalOcean
- Telegram bot token
- Telegram chat id администратора или группы
- строку подключения `DATABASE_URL`
- `DJANGO_SECRET_KEY`

## Переменные окружения

Пример файла `/opt/sistema_loialnosti/.env`:

```env
DJANGO_SECRET_KEY=very-secret-key
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=142.93.49.181,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://142.93.49.181
DATABASE_URL=postgres://referral_user:StrongPassword123!@127.0.0.1:5432/referral_mvp
TELEGRAM_BOT_TOKEN=telegram-token
TELEGRAM_ADMIN_CHAT_ID=-1001234567890
```

## Установка проекта

```bash
cd /opt
git clone https://github.com/slogotipomby1-del/sistema_loialnosti.git
cd /opt/sistema_loialnosti/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .[dev,prod]
```

## Подготовка Django

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## Systemd

Скопируйте готовые unit-файлы:

```bash
cp /opt/sistema_loialnosti/deploy/systemd/referral_admin.service /etc/systemd/system/referral_admin.service
cp /opt/sistema_loialnosti/deploy/systemd/referral_bot.service /etc/systemd/system/referral_bot.service
cp /opt/sistema_loialnosti/deploy/systemd/bonus_expiration_warning.service /etc/systemd/system/bonus_expiration_warning.service
cp /opt/sistema_loialnosti/deploy/systemd/bonus_expiration_warning.timer /etc/systemd/system/bonus_expiration_warning.timer
cp /opt/sistema_loialnosti/deploy/systemd/bonus_expiration.service /etc/systemd/system/bonus_expiration.service
cp /opt/sistema_loialnosti/deploy/systemd/bonus_expiration.timer /etc/systemd/system/bonus_expiration.timer
systemctl daemon-reload
systemctl enable --now referral_admin
systemctl enable --now referral_bot
systemctl enable --now bonus_expiration_warning.timer
systemctl enable --now bonus_expiration.timer
```

Что это даёт:

- каждый день в 10:00 отправляются предупреждения участникам, у кого бонусы сгорят через 30 дней
- каждый день в 10:15 система проводит сгорание просроченных бонусов

При желании время можно поменять прямо в `.timer` файлах.

## Nginx

Скопируйте конфиг:

```bash
cp /opt/sistema_loialnosti/deploy/nginx/referral_admin.conf /etc/nginx/sites-available/referral_admin.conf
ln -sf /etc/nginx/sites-available/referral_admin.conf /etc/nginx/sites-enabled/referral_admin.conf
nginx -t
systemctl restart nginx
```

## Проверка

```bash
systemctl status referral_admin --no-pager
systemctl status referral_bot --no-pager
systemctl status nginx --no-pager
systemctl status bonus_expiration_warning.timer --no-pager
systemctl status bonus_expiration.timer --no-pager
systemctl list-timers --all | grep bonus_expiration
ss -tlnp | grep :80
```

Ручная проверка новых команд:

```bash
cd /opt/sistema_loialnosti/backend
source .venv/bin/activate
python manage.py send_bonus_expiration_warnings
python manage.py expire_bonus_entries
```

## Firewall в DigitalOcean

Для админки должен быть открыт inbound:

- HTTP / TCP / 80 / All IPv4

Для SSH:

- SSH / TCP / 22 / All IPv4

## Текущий адрес админки

- `http://142.93.49.181/admin/`
- `http://142.93.49.181/health/`

## Следующий этап

Когда будете готовы, следующим логичным шагом будет:

- вынести админку на отдельный домен
- включить HTTPS
- подключить amoCRM на этапе 2
