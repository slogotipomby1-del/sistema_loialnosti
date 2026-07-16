# Bonus Reversal And Balance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add bonus reversal, manual balance correction, negative balances after reversals, and clearer admin/member history for the loyalty MVP.

**Architecture:** Keep the current Django data model centered on bonus entries and spend requests, but turn bonus entries into a typed ledger with positive and negative movements. Calculate participant balance from confirmed ledger entries and approved spend requests, then expose the richer history in both the bot and the admin panel.

**Tech Stack:** Django 5, aiogram, pytest, SQLite/PostgreSQL via Django ORM

---

### Task 1: Expand bonus ledger model into a typed operation journal

**Files:**
- Modify: `backend/apps/bonuses/models.py`
- Modify: `backend/apps/common/choices.py`
- Create: `backend/apps/bonuses/migrations/0005_*.py`
- Test: `backend/tests/test_bonus_history.py`
- Test: `backend/tests/test_bot_dashboard_data.py`

- [ ] Add operation type choices for accrual, reversal, expiration, and manual adjustment.
- [ ] Add fields to bonus ledger entries for operation type, signed comment/reason text, optional expiration date, and optional source note for reversals.
- [ ] Keep spend requests as a separate approved spending source for now, to avoid a risky full refactor in one step.
- [ ] Write tests proving the service layer can distinguish accruals from reversals and still compute signed balances correctly.

### Task 2: Recalculate participant balance from confirmed operations

**Files:**
- Modify: `backend/apps/bot/services.py`
- Modify: `backend/apps/adminpanel/admin.py`
- Test: `backend/tests/test_bot_dashboard_data.py`
- Test: `backend/tests/test_admin_panel.py`

- [ ] Introduce one shared balance calculation path based on ledger entries plus approved spend requests.
- [ ] Stop subtracting pending spend requests from visible balance, because pending requests are not yet confirmed spending.
- [ ] Allow the resulting balance to become negative after a reversal.
- [ ] Add tests for positive balance, zero balance, and negative balance after reversal.

### Task 3: Show richer bonus history in the bot

**Files:**
- Modify: `backend/apps/bot/services.py`
- Modify: `backend/apps/bot/ui.py`
- Modify: `backend/apps/bot/handlers/member.py`
- Test: `backend/tests/test_bonus_history.py`
- Test: `backend/tests/test_bot_ui.py`

- [ ] Return one combined chronological history for accruals, approved spendings, reversals, expirations, and manual corrections.
- [ ] Update the bot text so the user sees clear labels: начисление, списание, аннулирование, сгорание, корректировка.
- [ ] Add wording for negative balances that sounds calm and operational rather than alarming.
- [ ] Add tests for the new labels and negative balance text.

### Task 4: Add admin tools for reversal and manual correction

**Files:**
- Modify: `backend/apps/adminpanel/admin.py`
- Test: `backend/tests/test_admin_panel.py`
- Test: `backend/tests/test_admin_change_memo.py`

- [ ] Expose the bonus entry type in admin lists and forms.
- [ ] Add admin actions or a practical entry path for reversal and manual correction.
- [ ] Add admin guidance text explaining when a reversal creates a negative balance.
- [ ] Show participant balance consistently from the new shared calculation.

### Task 5: Verify and document the new business rule

**Files:**
- Modify: `docs/2026-07-15_Регламент_администратора_MVP.md`
- Modify: `docs/2026-07-15_Короткий_итог_MVP.md`
- Test: `backend/tests/test_smoke.py`

- [ ] Update the admin regulation so reversal and negative balance are explicitly described as normal business behavior.
- [ ] Update the short MVP summary with the new manual capabilities.
- [ ] Run the full test suite to verify the project still passes end to end.
