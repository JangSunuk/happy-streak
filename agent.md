# Project UPGRADE (Personal iOS App) — Agent Instructions (v2)

You are building a **personal, local-only iOS app** for habit tracking + a trading challenge tracker.
This app is **not** intended for App Store distribution. Keep everything offline-first and simple.

## 1) Product Goal

Build a lightweight “identity + streak” tracker that helps the user:
- Track core habits (exercise, reading, no masturbation, weekday no games)
- Track morning routine
- Track daily protein intake (default 100g/day)
- Track **stress index** and **abdominal pain index** (duodenitis symptom tracker)
- Track a **trading challenge**: “10,000,000 → 100,000,000” with **two tracks**:
  - KRW track
  - USD track
- Auto-calculate balances from trade return %
- Generate a clean post format for **Threads** (Meta Threads) and share it as a **new post** each time (no reply-thread chaining)

## 2) Hard Constraints (Must Follow)

1. **Not limited to 90 days.** Streaks are indefinite. (Optional: allow “cycles”, but not required.)
2. **Remove all overtime/late-work content.** No “overtime mode” or wording.
3. Target device: **iOS**.
4. **No distribution plan.** No analytics, no accounts, no server backend.
5. Notifications: only one style — if user hasn’t checked/logged for the day, send a reminder like:
   - Korean tone: **“오늘 체크를 안했어요!!”**
6. Trading module:
   - Default bet size = **100%** of current balance
   - Must include **bet % option** (0–100)
   - No fees/taxes options
   - Must support **two parallel challenge tracks** (KRW and USD)
7. Threads posting:
   - **Do NOT** implement “reply chain” posting.
   - Each share is a **separate new post** (share sheet / copy format).
   - Do **NOT** implement OAuth / Threads API unless explicitly requested later.
8. Include:
   - Trading “profit streak” (consecutive winning trades)
   - “rule violation” tracking (simple + fast)
9. Add **abdominal pain index** input (“배아픔지수”) to the daily log.
10. Remove any requirement that daily logging must be completed in < 60 seconds. (Still keep friction low.)

## 3) Day Boundary / Logical Date Rule (Very Important)

The app must allow a configurable **“day start time”** (e.g., 04:00).

### Requirement
- Add Settings option: **Day Start Time** (time-of-day, default 04:00).
- When the user logs data at night/early morning, the app should map it to the **logical day** based on that start time.

### Definition
Let:
- `now` = current DateTime
- `dayStartTime` = e.g., 04:00 local time

Compute **logicalDate** (the DailyLog date key):
- If `time(now) < dayStartTime`, then logicalDate = **calendar date of (now - 1 day)**.
- Else logicalDate = calendar date of now.

This logicalDate must be used consistently for:
- DailyLog creation/fetch
- Streak calculations
- Notification “did you log today?” checks
- Stats aggregation

## 4) Tech Stack Recommendation

- **Swift + SwiftUI**
- Local persistence:
  - Prefer **SwiftData** if targeting iOS 17+ (simpler).
  - If you need broader compatibility, use CoreData.
- Notifications:
  - `UNUserNotificationCenter` local notifications only.
- Sharing:
  - iOS Share Sheet (`ShareLink` / `UIActivityViewController`) and a “Copy” fallback.

## 5) Information Architecture (4 tabs max)

Use a tab bar with 4 tabs:

1) **Today**
2) **Trades**
3) **Stats**
4) **Settings**

Keep all daily input on **Today**.

## 6) Core Features — Habits & Health

### 6.1 Daily Habit Checklist (fixed items)
- 💪 Exercise (done / skipped / failed)
- 📚 Reading (done / skipped / failed)
- 🚫 No masturbation (done / failed)
- 🎮 Weekday no games (on weekdays only: done / failed)

Notes:
- “Skipped” should not count as done for streak logic, but should be recorded.
- Weekday rule: Monday–Friday (configurable in Settings if easy).

### 6.2 Morning Routine (simple 3 toggles)
- ⏰ Wake up on time (default goal: 07:00)
- 🍳 Breakfast done (carb + protein concept, just a boolean)
- 📈 Stock review done (record-only, no trading)

Award a small “Morning Win” badge if 2/3 completed (optional).

### 6.3 Protein Intake
- Default daily target: **100g**
- Input should be frictionless:
  - Quick add buttons: +10g, +20g, +30g
  - Optional manual entry
- Show progress bar and “Target hit!” state.

### 6.4 Stress Index (Daily)
- Simple 4-level picker:
  1) Low 😌
  2) Normal 🙂
  3) High 😐
  4) Very High 😣
- Optional “cause” multi-select:
  - Work, Relationships, Sleep, Loneliness, Health, Other

### 6.5 Abdominal Pain Index (Daily)
Because of duodenitis.
- Recommended:
  - 0–10 slider + optional note (“where/when/how long”)
- Add disclaimer text inside Settings:
  - “This is not medical advice. If symptoms worsen, seek professional care.”

### 6.6 Streak Logic (Indefinite)
Define:
- **Global streak**: day counts when user hits at least **3 of 4** main habit items
  - (Exercise, Reading, No masturbation, Weekday no games if applicable)
- Also keep individual streaks:
  - Exercise streak
  - Reading streak
  - No masturbation streak
  - Weekday no games streak (weekday-only)

No “overtime mode”.

### 6.7 Rule Violation Tracking
A lightweight system:
- On Today screen: “Rule violation today?” toggle.
- If yes:
  - Choose from a short list (editable in Settings) + optional note.
- In Stats:
  - Total violations
  - Last 7/30 days trend

Default rule list examples (editable):
- “Scrolled too late”
- “Impulse trade”
- “Broke diet”
- “Porn/sexual content”

## 7) Trading Challenge Module (Two tracks: KRW / USD)

### 7.1 Tracks
Implement two independent challenge tracks:
- **KRW Track**
- **USD Track**

Each track has its own:
- Start capital
- Target capital
- Trade list
- Balance series
- Win rate and profit streak

### 7.2 Default Challenge Settings (editable)
Provide defaults in Settings:
- KRW: start 10,000,000 KRW, target 100,000,000 KRW
- USD: start and target configurable (e.g., 10,000 USD → 100,000 USD)
Do not convert FX rates; treat tracks as separate ledgers.

### 7.3 Trade Entry Form (minimum fields)
Required:
- Date/time (default now)
- Track selection: KRW or USD
- Symbol / name (string)
- Side: Buy / Sell (매수 / 매도)
- Return % (float, allow negative)
Optional:
- Bet % (0–100, default 100)

No fees/taxes.

### 7.4 Balance Calculation (per track)
Let:
- `prevBalance` = last trade balance within selected track, else track start capital
- `betPct` default 100

Compute:
- `invested = prevBalance * (betPct / 100)`
- `pnl = invested * (returnPct / 100)`
- `newBalance = prevBalance + pnl`

Store prevBalance and newBalance per trade (auditable).

### 7.5 Trading Metrics (per track)
- Current balance
- Progress to target (progress bar)
- Overall return %
- Number of trades
- Win rate
- **Profit streak**: consecutive trades where `returnPct > 0`
  - Track current + best
- Best trade / worst trade (by return %)

### 7.6 Trade List UI
- Top-level segmented control: **KRW | USD**
- List trades newest first
- Each item shows:
  - Date
  - Symbol
  - Side
  - Return %
  - Balance after trade

Tap trade → detail screen:
- Full calculation breakdown
- “Copy post format”
- “Share to Threads” (new post)

## 8) Threads Posting / Sharing (No API required)

Do **not** implement OAuth / Threads API unless explicitly asked later.
Instead:
- Generate text in required format and share via iOS Share Sheet.
- Each share becomes a **new Threads post**.

### 8.1 Required Post Format
Base format:
- `"{SYMBOL} {매수|매도}, {RETURN}%"`
Example:
- `"TSLA 매수, +3.25%"`

Recommended extended format (toggle in Settings):
- Include track and balance:
  - `"[{TRACK}] {SYMBOL} {SIDE}, {RETURN}% | 잔고 {BALANCE} {CCY} | 승률 {WINRATE}% | 연승 {PROFIT_STREAK}"`

Provide:
- Copy button
- Share button

## 9) Notifications

Only one type: a daily reminder if the user hasn’t logged today (based on **logicalDate**).

Behavior:
- Ask permission once in onboarding or Settings.
- Schedule a daily notification at a fixed time (e.g., 21:30 local).
- When user completes Today logging (any meaningful input), cancel that day’s pending reminder.

Notification text (Korean):
- Title: “체크 알림”
- Body: “오늘 체크를 안했어요!!”

## 10) Settings

Settings should include:
- Protein goal (default 100g)
- Wake goal time (default 07:00)
- Reminder time (default 21:30)
- **Day Start Time (default 04:00)** (critical)
- Share format: base vs extended
- Weekday definition (optional)
- Trading track start/target settings:
  - KRW start/target
  - USD start/target
- Rule list editor (optional but recommended)

## 11) Data Model (SwiftData/CoreData)

Suggested models:

### DailyLog
- dateKey (Date representing logical calendar day; store as start-of-day)
- exerciseStatus (enum)
- readingStatus (enum)
- noMasturbationStatus (enum)
- weekdayNoGameStatus (enum, optional on weekends)
- proteinGrams (Int)
- wakeUpOnTime (Bool)
- breakfastDone (Bool)
- stockReviewDone (Bool)
- stressLevel (Int 1–4)
- stressCauses ([String])
- abdominalPain (Int 0–10)
- abdominalPainNote (String?)
- ruleViolated (Bool)
- ruleViolationTags ([String])
- ruleViolationNote (String?)

### Trade
- timestamp (Date)
- track (enum: KRW / USD)
- symbol (String)
- side (enum buy/sell)
- returnPct (Double)
- betPct (Double, default 100)
- prevBalance (Double)
- newBalance (Double)

### Settings
- proteinGoal (Int, default 100)
- wakeGoalTime (DateComponents or minutes)
- reminderTime (DateComponents)
- dayStartTime (DateComponents, default 04:00)
- shareFormatExtended (Bool)
- weekdayDefinition (optional)
- krwStartCapital, krwTargetCapital
- usdStartCapital, usdTargetCapital
- ruleCatalog ([String]) optional

## 12) Implementation Plan (Suggested)

1) Scaffold SwiftUI app with 4 tabs.
2) Implement Settings with dayStartTime and persistence.
3) Implement logicalDate mapping and verify all reads/writes use it.
4) Implement Today tab logging + streak calculations.
5) Implement Trades tab:
   - Track selector (KRW/USD)
   - Trade form + balance calculation per track
   - Profit streak + metrics
6) Implement share/copy formatted Threads post.
7) Implement Stats tab aggregates by logicalDate.
8) Implement notification rule based on logicalDate completion.

