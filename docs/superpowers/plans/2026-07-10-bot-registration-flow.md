# Bot Registration Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить в Telegram-бот понятный первый экран, пошаговую регистрацию участника и выдачу реферальной ссылки после успешной регистрации.

**Architecture:** Логику первого сценария держим в `apps.bot.handlers`, тексты и клавиатуры выносим в небольшие вспомогательные функции, состояние регистрации строим через FSM aiogram. После завершения регистрации используем существующий сервис `register_participant`, а ссылку собираем из username самого бота и сохранённого referral code.

**Tech Stack:** Python 3.12, Django 5, aiogram 3, pytest

---

### Task 1: Подготовить тексты и клавиатуры первого экрана

**Files:**
- Create: `backend/apps/bot/ui.py`
- Test: `backend/tests/test_bot_ui.py`

- [ ] **Step 1: Написать падающий тест на стартовый экран и меню после регистрации**
- [ ] **Step 2: Реализовать функции текстов и клавиатур**
- [ ] **Step 3: Прогнать тесты UI**

### Task 2: Добавить сценарий регистрации через FSM

**Files:**
- Modify: `backend/apps/bot/handlers/start.py`
- Modify: `backend/apps/bot/handlers/member.py`
- Test: `backend/tests/test_bot_registration_handlers.py`

- [ ] **Step 1: Написать падающий тест на шаги регистрации**
- [ ] **Step 2: Добавить состояния регистрации и обработчики имени, телефона и согласия**
- [ ] **Step 3: Прогнать тесты обработчиков**

### Task 3: Показать пользователю реферальную ссылку после регистрации

**Files:**
- Modify: `backend/apps/bot/handlers/member.py`
- Test: `backend/tests/test_bot_registration_handlers.py`

- [ ] **Step 1: Написать падающий тест на успешное завершение регистрации**
- [ ] **Step 2: Добавить сборку ссылки и финальное сообщение с кнопками**
- [ ] **Step 3: Прогнать тесты сценария и существующие тесты бота**
