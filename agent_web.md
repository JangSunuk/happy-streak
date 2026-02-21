# Project UPGRADE (Personal Local-Only Web App) — Agent Instructions

Build a personal, local-only web app that combines:
- Habit + health tracking (streak-based)
- Trading challenge tracker: 10,000,000 -> 100,000,000 with KRW and USD tracks

## Core Constraints

1. Streaks are indefinite.
2. Remove all overtime/late-work content.
3. No account/auth/backend/analytics.
4. Notifications: one reminder only when no meaningful log exists for logical day.
   - Title: "체크 알림"
   - Body: "오늘 체크를 안했어요!!"
5. Logical day based on configurable Day Start Time (default 04:00).
6. Trading:
   - bet% default 100, optional 0-100
   - no fees/taxes
   - KRW/USD fully separate ledgers
7. Threads sharing:
   - no reply-thread chaining
   - each share is independent new post style
   - MVP = copy/share text only

## Tabs (Max 4)

1. Today
2. Trades
3. Stats
4. Settings

## Today

- Habit checklist
  - Exercise: done/skipped/failed
  - Reading: done/skipped/failed
  - No masturbation: done/failed
  - Weekday no games: done/failed (weekdays only)
- Morning routine toggles
  - Wake up on time
  - Breakfast done
  - Stock review done
- Protein tracker
  - default target 100g/day
  - quick add +10/+20/+30
- Stress index
  - low/normal/high/very high
  - optional causes
- Abdominal pain index
  - 0-10 + optional note
- Rule violation
  - toggle + tags + note

## Trades

Required fields:
- timestamp
- track (KRW/USD)
- symbol/name
- side (buy/sell)
- return %

Optional:
- bet% (0-100, default 100)

Balance formula:
- prevBalance = last newBalance in track, else startCapital(track)
- invested = prevBalance * betPct/100
- pnl = invested * returnPct/100
- newBalance = prevBalance + pnl

Store prevBalance/newBalance on each trade.

Stats per track:
- current balance
- progress to target
- overall return %
- win rate
- profit streak (current + best)
- best/worst trade

## Settings

- Protein goal
- Wake goal time
- Reminder time
- Day Start Time
- KRW start/target
- USD start/target
- Share format toggle (base/extended)
- Rule tag editor
- Medical disclaimer text

## Logical Day Rule (Critical)

Given `now` and `dayStartTime`:
- if `time(now) < dayStartTime`, logicalDate = date(now - 1 day)
- else logicalDate = date(now)

Use this for:
- DailyLog create/fetch
- streaks
- reminder "logged today?"
- stats aggregation
