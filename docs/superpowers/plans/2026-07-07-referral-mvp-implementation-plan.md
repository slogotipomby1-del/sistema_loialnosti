# Referral MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build stage 1 of the referral MVP: Telegram bot for members and referred clients, browser admin panel for one administrator/owner, Telegram notifications about new applications, and manual bonus approval flows without amoCRM.

**Architecture:** Use a single Python monolith so the bot, admin panel, business rules, and database live in one codebase. Django handles the database, admin panel, and internal business logic; a small bot app inside the same project handles Telegram flows and writes into the same database. Background jobs are limited to lightweight notification sending and can start as synchronous calls where safe.

**Tech Stack:** Python 3.12, Django 5, PostgreSQL, aiogram 3, pytest, pytest-django

---

## Proposed File Structure

- `backend/pyproject.toml` - Python dependencies and project metadata
- `backend/manage.py` - Django entrypoint
- `backend/config/settings.py` - app settings, env variables, installed apps
- `backend/config/urls.py` - HTTP routes for admin and bot webhook
- `backend/config/asgi.py` - Django ASGI app
- `backend/config/wsgi.py` - Django WSGI app
- `backend/apps/users/models.py` - participant profile and Telegram identity
- `backend/apps/referrals/models.py` - referral link, referred lead, lead statuses
- `backend/apps/bonuses/models.py` - bonus ledger, balances, spend requests
- `backend/apps/bot/handlers/start.py` - start, consent, registration, referral entry
- `backend/apps/bot/handlers/member.py` - member menu, balance, referral link, history
- `backend/apps/bot/handlers/lead.py` - referred client application flow
- `backend/apps/bot/handlers/spend.py` - bonus spend request flow
- `backend/apps/bot/router.py` - bot router assembly
- `backend/apps/bot/services.py` - bot-to-domain orchestration
- `backend/apps/notifications/telegram.py` - outbound Telegram notifications to admin/owner
- `backend/apps/adminpanel/admin.py` - Django admin configuration for leads, users, bonuses
- `backend/apps/common/choices.py` - status constants and reusable enums
- `backend/apps/common/services.py` - small shared helpers
- `backend/tests/test_registration_flow.py` - registration behavior tests
- `backend/tests/test_referral_lead_flow.py` - referral attribution and lead creation tests
- `backend/tests/test_bonus_requests.py` - spend request and manual approval tests
- `backend/tests/test_admin_notifications.py` - notification dispatch tests
- `.env.example` - required environment variables without secrets
- `README.md` - setup and run instructions

## Task 1: Bootstrap The Monolith

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/manage.py`
- Create: `backend/config/__init__.py`
- Create: `backend/config/settings.py`
- Create: `backend/config/urls.py`
- Create: `backend/config/asgi.py`
- Create: `backend/config/wsgi.py`
- Create: `.env.example`
- Create: `README.md`

- [ ] **Step 1: Write the failing environment smoke test**

```python
# backend/tests/test_smoke.py
def test_smoke():
    assert True
```

- [ ] **Step 2: Run test to verify the project is not ready yet**

Run: `cd backend; pytest tests/test_smoke.py -v`
Expected: FAIL because `pytest` or the project dependencies are not installed yet.

- [ ] **Step 3: Write the minimal bootstrap files**

```toml
# backend/pyproject.toml
[project]
name = "referral-mvp"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "Django>=5.0,<5.1",
  "aiogram>=3.4,<3.5",
  "psycopg[binary]>=3.1,<3.2",
  "python-dotenv>=1.0,<2.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0,<9.0",
  "pytest-django>=4.8,<5.0",
]
```

```python
# backend/config/settings.py
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
```

```env
# .env.example
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgres://user:password@localhost:5432/referral_mvp
TELEGRAM_BOT_TOKEN=change-me
TELEGRAM_ADMIN_CHAT_ID=change-me
```

- [ ] **Step 4: Run smoke test to verify the bootstrap works**

Run: `cd backend; pytest tests/test_smoke.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/pyproject.toml backend/config backend/manage.py backend/tests/test_smoke.py .env.example README.md
git commit -m "chore: bootstrap referral mvp monolith"
```

## Task 2: Add Core Data Models And Status Rules

**Files:**
- Create: `backend/apps/common/choices.py`
- Create: `backend/apps/users/models.py`
- Create: `backend/apps/referrals/models.py`
- Create: `backend/apps/bonuses/models.py`
- Create: `backend/apps/users/apps.py`
- Create: `backend/apps/referrals/apps.py`
- Create: `backend/apps/bonuses/apps.py`
- Create: `backend/tests/test_referral_lead_flow.py`
- Modify: `backend/config/settings.py`

- [ ] **Step 1: Write the failing data-model test**

```python
# backend/tests/test_referral_lead_flow.py
import pytest

@pytest.mark.django_db
def test_lead_created_from_referral_keeps_referrer_relation():
    from apps.users.models import Participant
    from apps.referrals.models import ReferralLink, ReferralLead

    participant = Participant.objects.create(
        telegram_id="1001",
        full_name="Ivan Ivanov",
        phone="+375291112233",
        consent_accepted=True,
    )
    link = ReferralLink.objects.create(code="abc123", participant=participant)
    lead = ReferralLead.objects.create(
        referral_link=link,
        client_name="OOO Client",
        client_phone="+375291234567",
        status="new",
    )

    assert lead.referral_link.participant == participant
```

- [ ] **Step 2: Run the model test to verify it fails**

Run: `cd backend; pytest tests/test_referral_lead_flow.py::test_lead_created_from_referral_keeps_referrer_relation -v`
Expected: FAIL with import or model errors because the apps do not exist yet.

- [ ] **Step 3: Write the minimal models and choices**

```python
# backend/apps/common/choices.py
LEAD_STATUS_NEW = "new"
LEAD_STATUS_IN_PROGRESS = "in_progress"
LEAD_STATUS_ORDERED = "ordered"
LEAD_STATUS_BONUS_CONFIRMED = "bonus_confirmed"
LEAD_STATUS_REJECTED = "rejected"

LEAD_STATUS_CHOICES = [
    (LEAD_STATUS_NEW, "Новая"),
    (LEAD_STATUS_IN_PROGRESS, "В работе"),
    (LEAD_STATUS_ORDERED, "Клиент оформил заказ"),
    (LEAD_STATUS_BONUS_CONFIRMED, "Бонус подтверждён"),
    (LEAD_STATUS_REJECTED, "Отказ / не состоялось"),
]
```

```python
# backend/apps/users/models.py
from django.db import models

class Participant(models.Model):
    telegram_id = models.CharField(max_length=64, unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32)
    consent_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

```python
# backend/apps/referrals/models.py
from django.db import models
from apps.common.choices import LEAD_STATUS_CHOICES, LEAD_STATUS_NEW
from apps.users.models import Participant

class ReferralLink(models.Model):
    code = models.CharField(max_length=64, unique=True)
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)

class ReferralLead(models.Model):
    referral_link = models.ForeignKey(ReferralLink, null=True, blank=True, on_delete=models.SET_NULL)
    client_name = models.CharField(max_length=255)
    client_phone = models.CharField(max_length=32)
    status = models.CharField(max_length=32, choices=LEAD_STATUS_CHOICES, default=LEAD_STATUS_NEW)
    admin_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

```python
# backend/apps/bonuses/models.py
from django.db import models
from apps.users.models import Participant
from apps.referrals.models import ReferralLead

class BonusLedgerEntry(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    lead = models.ForeignKey(ReferralLead, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class BonusSpendRequest(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=32, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
```

- [ ] **Step 4: Run the model test to verify it passes**

Run: `cd backend; pytest tests/test_referral_lead_flow.py::test_lead_created_from_referral_keeps_referrer_relation -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/apps/common/choices.py backend/apps/users backend/apps/referrals backend/apps/bonuses backend/config/settings.py backend/tests/test_referral_lead_flow.py
git commit -m "feat: add referral and bonus domain models"
```

## Task 3: Implement Participant Registration And Referral Link Issuance

**Files:**
- Create: `backend/apps/bot/handlers/start.py`
- Create: `backend/apps/bot/router.py`
- Create: `backend/apps/bot/services.py`
- Create: `backend/tests/test_registration_flow.py`
- Modify: `backend/apps/users/models.py`
- Modify: `backend/apps/referrals/models.py`

- [ ] **Step 1: Write the failing registration service test**

```python
# backend/tests/test_registration_flow.py
import pytest

@pytest.mark.django_db
def test_register_participant_creates_referral_link():
    from apps.bot.services import register_participant
    from apps.referrals.models import ReferralLink

    participant = register_participant(
        telegram_id="1002",
        full_name="Petr Petrov",
        phone="+375299998877",
        consent_accepted=True,
    )

    assert ReferralLink.objects.filter(participant=participant).exists()
```

- [ ] **Step 2: Run the registration test to verify it fails**

Run: `cd backend; pytest tests/test_registration_flow.py::test_register_participant_creates_referral_link -v`
Expected: FAIL because `register_participant` does not exist yet.

- [ ] **Step 3: Write the minimal registration implementation**

```python
# backend/apps/bot/services.py
import secrets
from apps.users.models import Participant
from apps.referrals.models import ReferralLink

def register_participant(*, telegram_id: str, full_name: str, phone: str, consent_accepted: bool):
    participant, _ = Participant.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            "full_name": full_name,
            "phone": phone,
            "consent_accepted": consent_accepted,
        },
    )
    ReferralLink.objects.get_or_create(
        participant=participant,
        defaults={"code": secrets.token_urlsafe(8)},
    )
    return participant
```

```python
# backend/apps/bot/handlers/start.py
from aiogram import Router

router = Router(name="start")
```

```python
# backend/apps/bot/router.py
from aiogram import Router
from apps.bot.handlers import start

def build_router() -> Router:
    router = Router(name="root")
    router.include_router(start.router)
    return router
```

- [ ] **Step 4: Run the registration test to verify it passes**

Run: `cd backend; pytest tests/test_registration_flow.py::test_register_participant_creates_referral_link -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/apps/bot backend/tests/test_registration_flow.py backend/apps/users/models.py backend/apps/referrals/models.py
git commit -m "feat: add participant registration and referral link creation"
```

## Task 4: Implement Referred Client Application Flow And Admin Notification

**Files:**
- Create: `backend/apps/bot/handlers/lead.py`
- Create: `backend/apps/notifications/telegram.py`
- Create: `backend/tests/test_admin_notifications.py`
- Modify: `backend/apps/bot/services.py`
- Modify: `backend/apps/referrals/models.py`

- [ ] **Step 1: Write the failing lead creation and notification test**

```python
# backend/tests/test_admin_notifications.py
import pytest

@pytest.mark.django_db
def test_lead_creation_triggers_admin_notification(monkeypatch):
    from apps.bot.services import create_referral_lead
    from apps.users.models import Participant
    from apps.referrals.models import ReferralLink

    sent = {}

    def fake_send_admin_notification(text: str):
        sent["text"] = text

    monkeypatch.setattr("apps.notifications.telegram.send_admin_notification", fake_send_admin_notification)

    participant = Participant.objects.create(
        telegram_id="1003",
        full_name="Olga Petrova",
        phone="+375291111111",
        consent_accepted=True,
    )
    link = ReferralLink.objects.create(code="ref-1003", participant=participant)

    lead = create_referral_lead(
        referral_code=link.code,
        client_name="OOO New Client",
        client_phone="+375292222222",
    )

    assert lead.referral_link == link
    assert "OOO New Client" in sent["text"]
```

- [ ] **Step 2: Run the notification test to verify it fails**

Run: `cd backend; pytest tests/test_admin_notifications.py::test_lead_creation_triggers_admin_notification -v`
Expected: FAIL because the lead service and notification sender do not exist yet.

- [ ] **Step 3: Write the minimal lead flow and notification implementation**

```python
# backend/apps/notifications/telegram.py
def send_admin_notification(text: str) -> None:
    # Initial MVP implementation can send synchronously.
    return None
```

```python
# backend/apps/bot/services.py
from apps.notifications.telegram import send_admin_notification
from apps.referrals.models import ReferralLead, ReferralLink

def create_referral_lead(*, referral_code: str | None, client_name: str, client_phone: str):
    referral_link = ReferralLink.objects.filter(code=referral_code).first() if referral_code else None
    lead = ReferralLead.objects.create(
        referral_link=referral_link,
        client_name=client_name,
        client_phone=client_phone,
    )
    send_admin_notification(f"Новая заявка: {client_name}, {client_phone}")
    return lead
```

```python
# backend/apps/bot/handlers/lead.py
from aiogram import Router

router = Router(name="lead")
```

- [ ] **Step 4: Run the notification test to verify it passes**

Run: `cd backend; pytest tests/test_admin_notifications.py::test_lead_creation_triggers_admin_notification -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/apps/bot/handlers/lead.py backend/apps/notifications/telegram.py backend/apps/bot/services.py backend/tests/test_admin_notifications.py
git commit -m "feat: add referred lead intake and admin notification"
```

## Task 5: Implement Bonus Spend Requests And Manual Admin Control

**Files:**
- Create: `backend/apps/bot/handlers/spend.py`
- Create: `backend/tests/test_bonus_requests.py`
- Modify: `backend/apps/bonuses/models.py`
- Modify: `backend/apps/bot/services.py`
- Modify: `backend/apps/adminpanel/admin.py`

- [ ] **Step 1: Write the failing spend-request test**

```python
# backend/tests/test_bonus_requests.py
import pytest
from decimal import Decimal

@pytest.mark.django_db
def test_member_can_create_bonus_spend_request():
    from apps.bot.services import create_bonus_spend_request
    from apps.users.models import Participant

    participant = Participant.objects.create(
        telegram_id="1004",
        full_name="Anna Sidorova",
        phone="+375293333333",
        consent_accepted=True,
    )

    request = create_bonus_spend_request(participant=participant, amount=Decimal("50.00"))

    assert request.status == "pending"
    assert request.amount == Decimal("50.00")
```

- [ ] **Step 2: Run the spend-request test to verify it fails**

Run: `cd backend; pytest tests/test_bonus_requests.py::test_member_can_create_bonus_spend_request -v`
Expected: FAIL because the spend request service does not exist yet.

- [ ] **Step 3: Write the minimal spend-request implementation and admin control**

```python
# backend/apps/bot/services.py
from decimal import Decimal
from apps.bonuses.models import BonusSpendRequest

def create_bonus_spend_request(*, participant, amount: Decimal):
    return BonusSpendRequest.objects.create(
        participant=participant,
        amount=amount,
        status="pending",
    )
```

```python
# backend/apps/adminpanel/admin.py
from django.contrib import admin
from apps.referrals.models import ReferralLead
from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
from apps.users.models import Participant

admin.site.register(Participant)
admin.site.register(ReferralLead)
admin.site.register(BonusLedgerEntry)
admin.site.register(BonusSpendRequest)
```

```python
# backend/apps/bot/handlers/spend.py
from aiogram import Router

router = Router(name="spend")
```

- [ ] **Step 4: Run the spend-request test to verify it passes**

Run: `cd backend; pytest tests/test_bonus_requests.py::test_member_can_create_bonus_spend_request -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/apps/bot/handlers/spend.py backend/apps/adminpanel/admin.py backend/apps/bot/services.py backend/tests/test_bonus_requests.py
git commit -m "feat: add bonus spend requests and admin controls"
```

## Task 6: Assemble Admin Panel, Bot Menus, And MVP Readiness Checks

**Files:**
- Create: `backend/apps/bot/handlers/member.py`
- Modify: `backend/apps/bot/router.py`
- Modify: `backend/config/urls.py`
- Modify: `README.md`
- Modify: `.env.example`
- Modify: `backend/tests/test_registration_flow.py`
- Modify: `backend/tests/test_referral_lead_flow.py`
- Modify: `backend/tests/test_bonus_requests.py`
- Modify: `backend/tests/test_admin_notifications.py`

- [ ] **Step 1: Write the failing end-to-end service coverage test**

```python
# extend backend/tests/test_registration_flow.py
import pytest

@pytest.mark.django_db
def test_registered_participant_has_data_needed_for_member_menu():
    from apps.bot.services import register_participant
    from apps.referrals.models import ReferralLink

    participant = register_participant(
        telegram_id="1005",
        full_name="Sergey Kozlov",
        phone="+375294444444",
        consent_accepted=True,
    )

    link = ReferralLink.objects.get(participant=participant)
    assert participant.full_name == "Sergey Kozlov"
    assert link.code
```

- [ ] **Step 2: Run the focused test suite to verify gaps remain**

Run: `cd backend; pytest tests/test_registration_flow.py tests/test_referral_lead_flow.py tests/test_bonus_requests.py tests/test_admin_notifications.py -v`
Expected: FAIL until the router, menu wiring, and final settings are connected.

- [ ] **Step 3: Wire the final MVP surfaces**

```python
# backend/apps/bot/handlers/member.py
from aiogram import Router

router = Router(name="member")
```

```python
# backend/apps/bot/router.py
from aiogram import Router
from apps.bot.handlers import lead, member, spend, start

def build_router() -> Router:
    router = Router(name="root")
    router.include_router(start.router)
    router.include_router(member.router)
    router.include_router(lead.router)
    router.include_router(spend.router)
    return router
```

```python
# backend/config/urls.py
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
```

```markdown
# README.md
## MVP Scope
- Telegram bot for participants and referred clients
- Browser admin panel for one administrator/owner
- Telegram notifications on new leads
- Manual bonus approvals and spend approvals
```

- [ ] **Step 4: Run the focused test suite to verify the MVP shell passes**

Run: `cd backend; pytest tests/test_registration_flow.py tests/test_referral_lead_flow.py tests/test_bonus_requests.py tests/test_admin_notifications.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/apps/bot/handlers/member.py backend/apps/bot/router.py backend/config/urls.py README.md .env.example backend/tests
git commit -m "feat: assemble referral mvp application shell"
```

## Self-Review

### Spec Coverage

- Participant registration and referral link: covered by Task 3
- New client lead creation from referral link: covered by Task 4
- Admin notification in Telegram: covered by Task 4
- Closed browser admin panel: covered by Tasks 5 and 6
- Manual statuses and manual bonus confirmation: covered by Tasks 2 and 5
- Bonus spend request from bot: covered by Task 5
- Stage 1 excludes amoCRM: preserved in all tasks by omission

### Placeholder Scan

- No `TODO`, `TBD`, or “implement later” placeholders are intentionally left in the plan
- One open engineering assumption remains explicit: Django monolith with aiogram inside one repo

### Type Consistency

- `Participant`, `ReferralLink`, `ReferralLead`, `BonusLedgerEntry`, and `BonusSpendRequest` use the same names across tasks
- Lead status values stay consistent between choices and model defaults
- Service names stay consistent: `register_participant`, `create_referral_lead`, `create_bonus_spend_request`
