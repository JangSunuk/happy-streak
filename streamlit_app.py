from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, date, time, timedelta
from pathlib import Path
from typing import Any

import streamlit as st

DATA_PATH = Path(__file__).with_name("data.json")

DEFAULTS: dict[str, Any] = {
    "settings": {
        "proteinGoal": 100,
        "wakeGoalTime": "07:00",
        "reminderTime": "21:30",
        "dayStartTime": "04:00",
        "krwStartCapital": 10_000_000.0,
        "krwTargetCapital": 100_000_000.0,
        "usdStartCapital": 10_000.0,
        "usdTargetCapital": 100_000.0,
        "shareExtendedFormat": False,
        "ruleTags": [
            "Scrolled too late",
            "Impulse trade",
            "Broke diet",
            "Porn/sexual content",
        ],
    },
    "dailyLogs": {},
    "trades": [],
}

STRESS_MAP = {"low": 1, "normal": 2, "high": 3, "very high": 4}


def load_data() -> dict[str, Any]:
    if not DATA_PATH.exists():
        return json.loads(json.dumps(DEFAULTS))
    try:
        raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return json.loads(json.dumps(DEFAULTS))

    merged = json.loads(json.dumps(DEFAULTS))
    merged.update(raw)
    merged["settings"].update(raw.get("settings", {}))
    return merged


def save_data(data: dict[str, Any]) -> None:
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_hhmm(hhmm: str) -> time:
    h, m = hhmm.split(":")
    return time(hour=int(h), minute=int(m))


def logical_date(now: datetime, day_start_hhmm: str) -> date:
    day_start = parse_hhmm(day_start_hhmm)
    pivot = datetime.combine(now.date(), day_start)
    if now < pivot:
        return now.date() - timedelta(days=1)
    return now.date()


def date_key(d: date) -> str:
    return d.isoformat()


def is_weekday(d: date) -> bool:
    return d.weekday() < 5


def empty_log(d: date) -> dict[str, Any]:
    return {
        "date": date_key(d),
        "exerciseStatus": "failed",
        "readingStatus": "failed",
        "noMasturbationStatus": "failed",
        "weekdayNoGameStatus": "failed" if is_weekday(d) else None,
        "wakeUpOnTime": False,
        "breakfastDone": False,
        "stockReviewDone": False,
        "proteinGrams": 0,
        "stressLevel": "",
        "stressCauses": [],
        "abdominalPainIndex": 0,
        "abdominalPainNote": "",
        "ruleViolated": False,
        "ruleViolationTags": [],
        "ruleViolationNote": "",
        "updatedAt": datetime.now().isoformat(),
    }


def get_or_create_log(data: dict[str, Any], d: date) -> dict[str, Any]:
    key = date_key(d)
    logs = data["dailyLogs"]
    if key not in logs:
        logs[key] = empty_log(d)
    return logs[key]


def has_meaningful(log: dict[str, Any]) -> bool:
    return any(
        [
            log.get("exerciseStatus") != "failed",
            log.get("readingStatus") != "failed",
            log.get("noMasturbationStatus") == "done",
            log.get("weekdayNoGameStatus") == "done",
            bool(log.get("wakeUpOnTime")),
            bool(log.get("breakfastDone")),
            bool(log.get("stockReviewDone")),
            int(log.get("proteinGrams", 0)) > 0,
            bool(log.get("stressLevel")),
            int(log.get("abdominalPainIndex", 0)) > 0,
            bool(log.get("abdominalPainNote", "")),
            bool(log.get("ruleViolated")),
            len(log.get("ruleViolationTags", [])) > 0,
            bool(log.get("ruleViolationNote", "")),
        ]
    )


def track_start(data: dict[str, Any], track: str) -> float:
    return float(data["settings"]["krwStartCapital"] if track == "KRW" else data["settings"]["usdStartCapital"])


def track_target(data: dict[str, Any], track: str) -> float:
    return float(data["settings"]["krwTargetCapital"] if track == "KRW" else data["settings"]["usdTargetCapital"])


def track_trades(data: dict[str, Any], track: str) -> list[dict[str, Any]]:
    return sorted(
        [t for t in data["trades"] if t["track"] == track],
        key=lambda x: x["timestamp"],
    )


@dataclass
class TradeStats:
    current_balance: float
    progress: float
    overall_return_pct: float
    win_rate: float
    current_profit_streak: int
    best_profit_streak: int
    best_trade: dict[str, Any] | None
    worst_trade: dict[str, Any] | None


def trade_stats(data: dict[str, Any], track: str) -> TradeStats:
    trades = track_trades(data, track)
    start = track_start(data, track)
    target = track_target(data, track)
    current = trades[-1]["newBalance"] if trades else start

    wins = [t for t in trades if t["returnPct"] > 0]
    win_rate = (len(wins) / len(trades) * 100) if trades else 0

    curr = 0
    for t in reversed(trades):
        if t["returnPct"] > 0:
            curr += 1
        else:
            break

    best = 0
    run = 0
    for t in trades:
        if t["returnPct"] > 0:
            run += 1
            best = max(best, run)
        else:
            run = 0

    best_trade = max(trades, key=lambda t: t["returnPct"], default=None)
    worst_trade = min(trades, key=lambda t: t["returnPct"], default=None)

    denom = (target - start) if target != start else 1.0
    progress = max(0.0, min(1.0, (current - start) / denom))
    overall = ((current - start) / start * 100) if start != 0 else 0

    return TradeStats(
        current_balance=current,
        progress=progress,
        overall_return_pct=overall,
        win_rate=win_rate,
        current_profit_streak=curr,
        best_profit_streak=best,
        best_trade=best_trade,
        worst_trade=worst_trade,
    )


def streak_count(data: dict[str, Any], check_fn) -> int:
    settings = data["settings"]
    d = logical_date(datetime.now(), settings["dayStartTime"])
    n = 0
    while True:
        key = date_key(d)
        log = data["dailyLogs"].get(key)
        if not log:
            break
        if not check_fn(d, log):
            break
        n += 1
        d = d - timedelta(days=1)
    return n


def global_hit(d: date, log: dict[str, Any]) -> bool:
    done = 0
    total = 3
    if log["exerciseStatus"] == "done":
        done += 1
    if log["readingStatus"] == "done":
        done += 1
    if log["noMasturbationStatus"] == "done":
        done += 1
    if is_weekday(d):
        total += 1
        if log.get("weekdayNoGameStatus") == "done":
            done += 1
    return done >= min(3, total)


def share_text(data: dict[str, Any], trade: dict[str, Any]) -> str:
    side = "매수" if trade["side"] == "buy" else "매도"
    base = f"{trade['symbol']} {side}, {trade['returnPct']:.2f}%"
    if not data["settings"]["shareExtendedFormat"]:
        return base
    stats = trade_stats(data, trade["track"])
    ccy = trade["track"]
    return (
        f"[{trade['track']}] {base} | 잔고 {trade['newBalance']:.2f} {ccy} "
        f"| 승률 {stats.win_rate:.1f}% | 연승 {stats.current_profit_streak}"
    )


def render_today(data: dict[str, Any]) -> None:
    st.subheader("Today")
    now = datetime.now()
    d = logical_date(now, data["settings"]["dayStartTime"])
    log = get_or_create_log(data, d)

    st.caption(f"Logical Date: {d.isoformat()} | Day Start: {data['settings']['dayStartTime']}")

    c1, c2 = st.columns(2)
    with c1:
        log["exerciseStatus"] = st.selectbox("Exercise", ["done", "skipped", "failed"], index=["done", "skipped", "failed"].index(log["exerciseStatus"]))
        log["readingStatus"] = st.selectbox("Reading", ["done", "skipped", "failed"], index=["done", "skipped", "failed"].index(log["readingStatus"]))
        log["noMasturbationStatus"] = st.selectbox("No masturbation", ["done", "failed"], index=["done", "failed"].index(log["noMasturbationStatus"]))
        if is_weekday(d):
            val = log.get("weekdayNoGameStatus") or "failed"
            log["weekdayNoGameStatus"] = st.selectbox("Weekday no games", ["done", "failed"], index=["done", "failed"].index(val))
        else:
            st.info("Weekday no games: N/A on weekends")

        log["wakeUpOnTime"] = st.checkbox("Wake up on time", value=bool(log["wakeUpOnTime"]))
        log["breakfastDone"] = st.checkbox("Breakfast done", value=bool(log["breakfastDone"]))
        log["stockReviewDone"] = st.checkbox("Stock review done", value=bool(log["stockReviewDone"]))

    with c2:
        log["proteinGrams"] = st.number_input("Protein grams", min_value=0, max_value=500, value=int(log["proteinGrams"]), step=1)
        add = st.radio("Quick add", [0, 10, 20, 30], horizontal=True)
        if add:
            log["proteinGrams"] = int(log["proteinGrams"]) + int(add)

        stress_levels = ["", "low", "normal", "high", "very high"]
        log["stressLevel"] = st.selectbox("Stress index", stress_levels, index=stress_levels.index(log.get("stressLevel", "")))
        causes = ["work", "relationships", "sleep", "loneliness", "health", "other"]
        log["stressCauses"] = st.multiselect("Stress causes", causes, default=log.get("stressCauses", []))

        log["abdominalPainIndex"] = st.slider("Abdominal pain index", 0, 10, int(log.get("abdominalPainIndex", 0)))
        log["abdominalPainNote"] = st.text_area("Abdominal pain note", value=log.get("abdominalPainNote", ""))

        log["ruleViolated"] = st.checkbox("Rule violated today?", value=bool(log.get("ruleViolated", False)))
        if log["ruleViolated"]:
            log["ruleViolationTags"] = st.multiselect("Violation tags", data["settings"]["ruleTags"], default=log.get("ruleViolationTags", []))
            log["ruleViolationNote"] = st.text_area("Violation note", value=log.get("ruleViolationNote", ""), key="viol_note")
        else:
            log["ruleViolationTags"] = []
            log["ruleViolationNote"] = ""

    if st.button("Save Today Log", type="primary"):
        log["updatedAt"] = datetime.now().isoformat()
        data["dailyLogs"][date_key(d)] = log
        save_data(data)
        st.success("Saved")


def render_trades(data: dict[str, Any]) -> None:
    st.subheader("Trades")
    track = st.segmented_control("Track", ["KRW", "USD"], default="KRW")

    with st.form("add_trade", clear_on_submit=True):
        ts = st.datetime_input("Timestamp", value=datetime.now())
        symbol = st.text_input("Symbol/Name")
        side = st.selectbox("Side", ["buy", "sell"])
        return_pct = st.number_input("Return %", value=0.0, step=0.1, format="%.2f")
        bet_pct = st.number_input("Bet %", min_value=0.0, max_value=100.0, value=100.0, step=1.0)
        submitted = st.form_submit_button("Save Trade", type="primary")

    if submitted:
        if not symbol.strip():
            st.error("Symbol is required")
        else:
            existing = track_trades(data, track)
            prev = float(existing[-1]["newBalance"]) if existing else track_start(data, track)
            invested = prev * (bet_pct / 100)
            pnl = invested * (return_pct / 100)
            new_balance = prev + pnl
            data["trades"].append(
                {
                    "timestamp": ts.isoformat(),
                    "track": track,
                    "symbol": symbol.strip(),
                    "side": side,
                    "returnPct": float(return_pct),
                    "betPct": float(bet_pct),
                    "prevBalance": prev,
                    "newBalance": new_balance,
                }
            )
            save_data(data)
            st.success("Trade saved")

    stats = trade_stats(data, track)
    a, b, c = st.columns(3)
    a.metric("Current Balance", f"{stats.current_balance:,.2f} {track}")
    b.metric("Progress", f"{stats.progress * 100:.1f}%")
    c.metric("Win Rate", f"{stats.win_rate:.1f}%")

    st.write(
        f"Overall Return: {stats.overall_return_pct:.2f}% | "
        f"Profit Streak: {stats.current_profit_streak} (best {stats.best_profit_streak})"
    )

    rows = list(reversed(track_trades(data, track)))
    if not rows:
        st.info("No trades yet")
        return

    for i, t in enumerate(rows):
        st.markdown(
            f"**{t['symbol']}** {'매수' if t['side'] == 'buy' else '매도'}, {t['returnPct']:.2f}%  \n"
            f"{datetime.fromisoformat(t['timestamp']).strftime('%Y-%m-%d %H:%M')} | "
            f"Bet {t['betPct']:.1f}% | Prev {t['prevBalance']:.2f} -> New {t['newBalance']:.2f} {track}"
        )
        txt = share_text(data, t)
        st.code(txt)
        st.caption("Copy above text for Threads post")
        if i < len(rows) - 1:
            st.divider()


def recent_logs(data: dict[str, Any], days: int) -> list[tuple[date, dict[str, Any]]]:
    d = logical_date(datetime.now(), data["settings"]["dayStartTime"])
    out = []
    for _ in range(days):
        key = date_key(d)
        if key in data["dailyLogs"]:
            out.append((d, data["dailyLogs"][key]))
        d -= timedelta(days=1)
    return out


def render_stats(data: dict[str, Any]) -> None:
    st.subheader("Stats")

    global_s = streak_count(data, lambda d, l: global_hit(d, l))
    exercise_s = streak_count(data, lambda _, l: l["exerciseStatus"] == "done")
    reading_s = streak_count(data, lambda _, l: l["readingStatus"] == "done")
    nom_s = streak_count(data, lambda _, l: l["noMasturbationStatus"] == "done")
    games_s = streak_count(data, lambda d, l: (not is_weekday(d)) or (l.get("weekdayNoGameStatus") == "done"))

    c1, c2, c3 = st.columns(3)
    c1.metric("Global Streak", global_s)
    c1.metric("Exercise", exercise_s)
    c2.metric("Reading", reading_s)
    c2.metric("No Masturbation", nom_s)
    c3.metric("Weekday No Games", games_s)

    logs = list(data["dailyLogs"].values())
    total_viol = sum(1 for l in logs if l.get("ruleViolated"))
    l7 = recent_logs(data, 7)
    l30 = recent_logs(data, 30)
    viol7 = sum(1 for _, l in l7 if l.get("ruleViolated"))
    viol30 = sum(1 for _, l in l30 if l.get("ruleViolated"))

    st.write(f"Rule violations: total {total_viol}, 7d {viol7}, 30d {viol30}")

    stress_vals = [STRESS_MAP.get(l.get("stressLevel", "")) for _, l in l7 if l.get("stressLevel")]
    stress_vals = [v for v in stress_vals if v is not None]
    pain_vals = [int(l.get("abdominalPainIndex", 0)) for _, l in l7]

    avg_stress = sum(stress_vals) / len(stress_vals) if stress_vals else 0
    avg_pain = sum(pain_vals) / len(pain_vals) if pain_vals else 0
    st.write(f"Avg stress (7d): {avg_stress:.2f} | Avg abdominal pain (7d): {avg_pain:.2f}")

    krw = trade_stats(data, "KRW")
    usd = trade_stats(data, "USD")
    st.write(
        f"KRW balance {krw.current_balance:,.0f} / profit streak {krw.current_profit_streak} (best {krw.best_profit_streak})"
    )
    st.write(
        f"USD balance {usd.current_balance:,.2f} / profit streak {usd.current_profit_streak} (best {usd.best_profit_streak})"
    )


def render_settings(data: dict[str, Any]) -> None:
    st.subheader("Settings")
    s = data["settings"]

    with st.form("settings_form"):
        s["proteinGoal"] = st.number_input("Protein goal", min_value=0, value=int(s["proteinGoal"]))
        s["wakeGoalTime"] = st.text_input("Wake goal time (HH:MM)", value=s["wakeGoalTime"])
        s["reminderTime"] = st.text_input("Reminder time (HH:MM)", value=s["reminderTime"])
        s["dayStartTime"] = st.text_input("Day start time (HH:MM)", value=s["dayStartTime"])

        s["krwStartCapital"] = st.number_input("KRW start", value=float(s["krwStartCapital"]))
        s["krwTargetCapital"] = st.number_input("KRW target", value=float(s["krwTargetCapital"]))
        s["usdStartCapital"] = st.number_input("USD start", value=float(s["usdStartCapital"]))
        s["usdTargetCapital"] = st.number_input("USD target", value=float(s["usdTargetCapital"]))

        s["shareExtendedFormat"] = st.checkbox("Use extended share format", value=bool(s["shareExtendedFormat"]))

        current_tags = st.text_area("Rule tags (one per line)", value="\n".join(s["ruleTags"]))
        submitted = st.form_submit_button("Save Settings", type="primary")

    st.caption("This is not medical advice. If symptoms worsen, seek professional care.")
    st.info("Reminder text: 체크 알림 / 오늘 체크를 안했어요!!")

    if submitted:
        s["ruleTags"] = [line.strip() for line in current_tags.splitlines() if line.strip()]
        save_data(data)
        st.success("Settings saved")


def reminder_hint(data: dict[str, Any]) -> None:
    d = logical_date(datetime.now(), data["settings"]["dayStartTime"])
    log = get_or_create_log(data, d)
    if not has_meaningful(log):
        st.warning("체크 알림: 오늘 체크를 안했어요!!")


def main() -> None:
    st.set_page_config(page_title="Happy Streak", page_icon="📈", layout="wide")
    st.title("Happy Streak (Streamlit)")
    st.caption("Local-only habit + trade tracker")

    data = load_data()
    reminder_hint(data)

    tabs = st.tabs(["Today", "Trades", "Stats", "Settings"])
    with tabs[0]:
        render_today(data)
    with tabs[1]:
        render_trades(data)
    with tabs[2]:
        render_stats(data)
    with tabs[3]:
        render_settings(data)


if __name__ == "__main__":
    main()
