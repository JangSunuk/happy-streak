# Project UPGRADE (Personal Local-Only iOS App) — Agent Instructions (v3)

Build a personal, offline-only iOS app (SwiftUI) that combines:
- Habit + health tracking (streak-based)
- Trading challenge tracker: 10,000,000 -> 100,000,000 with KRW and USD tracks

This app is not for App Store distribution.
Do not add accounts, analytics, or server/backend features.

## 1) Non-Negotiable Product Constraints

1. Streaks are indefinite. No 90-day limit.
2. Remove all overtime/late-work concepts and wording.
3. Platform target: iOS.
4. Local-only architecture. No login/account/backend.
5. Notifications: only one reminder type.
   - Trigger: user has not logged meaningful input for the logical day.
   - Title: "체크 알림"
   - Body: "오늘 체크를 안했어요!!"
6. Remove the acceptance requirement "daily logging must be under 60 seconds".
   - Keep UX simple and low-friction anyway.

## 2) Critical Rule: Logical Day via Day Start Time

### 2.1 Settings Requirement
Add `Day Start Time` in Settings.
- Default: `04:00`

### 2.2 Logical Date Definition
Given current local time `now` and `dayStartTime`:
- If `time(now) < dayStartTime`, then `logicalDate = calendarDate(now - 1 day)`
- Else `logicalDate = calendarDate(now)`

### 2.3 Mandatory Usage Scope
Use the same `logicalDate` rule for all of the following:
- DailyLog creation/fetch
- Streak calculations
- "Did user log today?" reminder logic
- Stats aggregation

## 3) App Information Architecture (Max 4 Tabs)

Use exactly these tabs:
1. Today
2. Trades
3. Stats
4. Settings

## 4) Today Tab: Habits + Health

### 4.1 Fixed Habit Checklist
- Exercise: `done | skipped | failed`
- Reading: `done | skipped | failed`
- No masturbation: `done | failed`
- Weekday no games: `done | failed` (weekdays only; weekends = N/A)

Streak logic:
- Global streak counts when >= 3 of 4 main habit items are completed.
- On weekends, weekday-no-games is excluded from denominator.
- Keep individual streaks per item.

### 4.2 Morning Routine (3 toggles)
- Wake up on time (goal time configurable)
- Breakfast done
- Stock review done (review-only record)

### 4.3 Protein Tracker
- Default target: `100g/day`
- Quick add: `+10`, `+20`, `+30`
- Optional manual input

### 4.4 Stress Index (Daily)
- 4-level scale: `low | normal | high | very high`
- Optional cause multi-select

### 4.5 Abdominal Pain Index (Daily)
- Recommended UI: `0-10` slider + optional note
- Purpose: duodenitis symptom tracking
- Add disclaimer in Settings: not medical advice

### 4.6 Rule Violation (Daily)
- Toggle: "Rule violated today?"
- If yes: choose tags from short list + optional note
- Stats must show total and trend

## 5) Trades Tab: KRW & USD Dual Tracks

### 5.1 Track Model
Two independent ledgers (no FX conversion):
- KRW track: default `10,000,000 -> 100,000,000 KRW`
- USD track: start/target configurable

### 5.2 Trade Input Fields
Required:
- timestamp
- track (`KRW | USD`)
- symbol/name
- side (`buy | sell`)
- return %

Optional:
- bet % (`0..100`, default `100`)

### 5.3 Balance Calculation (Per Track)
- `prevBalance = last newBalance in selected track; if none, startCapital(track)`
- `invested = prevBalance * (betPct / 100)`
- `pnl = invested * (returnPct / 100)`
- `newBalance = prevBalance + pnl`

Store both `prevBalance` and `newBalance` per trade.
No fees/taxes.

### 5.4 Per-Track Stats
- current balance
- progress to target
- overall return %
- win rate
- profit streak (`return% > 0`): current + best
- best/worst trade

### 5.5 Sharing (Threads-Compatible, No API)
- Do not implement reply-thread chaining.
- Each share is an independent new post.
- MVP sharing: Copy text + iOS Share Sheet only.

Base format:
- `"{SYMBOL} {매수|매도}, {RETURN}%"`

Optional extended format (toggle in Settings):
- include track and balance context

## 6) Settings Tab (Required)

Must include:
- Protein goal (default `100`)
- Wake goal time (default `07:00`)
- Reminder time (default `21:30`)
- Day Start Time (default `04:00`) [critical]
- KRW start/target capital
- USD start/target capital
- Share format toggle (base vs extended)
- Optional: edit rule-violation tag list
- Medical disclaimer text for abdominal pain tracker

## 7) Local Notifications

Implement one daily reminder only:
- At user-configured reminder time, notify only if no meaningful log exists for current logical day.
- After meaningful logging for that logical day, cancel/suppress that day's reminder.

Message:
- Title: "체크 알림"
- Body: "오늘 체크를 안했어요!!"

## 8) Persistence (Local Only)

Use SwiftData (preferred for iOS 17+) or CoreData.

## 9) Data Models (Minimum)

### DailyLog (keyed by logicalDate)
- logicalDate
- exerciseStatus
- readingStatus
- noMasturbationStatus
- weekdayNoGameStatus
- wakeUpOnTime
- breakfastDone
- stockReviewDone
- proteinGrams
- stressLevel
- stressCauses
- abdominalPainIndex
- abdominalPainNote
- ruleViolated
- ruleViolationTags
- ruleViolationNote

### Trade
- timestamp
- track (`KRW | USD`)
- symbol
- side (`buy | sell`)
- returnPct
- betPct (default 100)
- prevBalance
- newBalance

### AppSettings
- proteinGoal
- wakeGoalTime
- reminderTime
- dayStartTime
- krwStartCapital
- krwTargetCapital
- usdStartCapital
- usdTargetCapital
- shareExtendedFormat
- ruleViolationTagCatalog

## 10) Acceptance Checklist

1. Logging at `02:00` with dayStart `04:00` is stored in previous logical day.
2. Streak/stat/reminder behavior matches the same logical-day mapping.
3. Only one reminder type exists and uses exact Korean body text.
4. Trade calculation uses bet% default 100 and allows custom 0-100.
5. KRW and USD balances/statistics remain fully independent.
6. Profit streak is visible (current + best) per track.
7. Rule violation, stress index, abdominal pain index are recorded daily and reflected in stats.
8. No overtime-related feature/text exists.
9. No backend/account/analytics code exists.
