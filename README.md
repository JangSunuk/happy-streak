# Happy Streak (Streamlit, Local-Only)

개인용 로컬 앱:
- 습관/건강 스트릭 추적
- 트레이딩 챌린지(KRW/USD 독립 트랙)

서버/계정/분석 없음.

## 실행

```bash
cd /home/sunuk/code/happy-streak
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-streamlit.txt
streamlit run streamlit_app.py
```

## 현재 구조

- `streamlit_app.py` : 메인 앱
- `requirements-streamlit.txt` : 의존성
- `agent.md` / `agent_v2.md` / `agent_web.md` : 요구사항 문서
- `data.json` : 실행 후 생성되는 로컬 데이터 파일

## 핵심 기능

- 탭 4개: Today / Trades / Stats / Settings
- Day Start Time(기본 04:00) 기반 logical day
- 습관/건강(스트레스, 배아픔지수 포함)/규칙위반 일일 기록
- KRW/USD 분리 원장, bet% 기본 100(0~100)
- 수익 연승(current/best), 승률, best/worst trade
- Threads 공유 문구(base/extended)
- 알림 문구(앱 내 표시):
  - `체크 알림`
  - `오늘 체크를 안했어요!!`
