# 중간과제: 국가 간 아동 건강 격차 (2000–2020)

## 먼저 열 파일
1. `report.md`: 보고서 (데이터 출처·결합, 설계 근거, 한계, 가산점 신청)
2. `site/dashboard.html`: Part A 탐색형 대시보드. 브라우저로 열기 (인터넷 연결 필요: Vega 라이브러리를 CDN에서 불러옴)
3. `site/story.html`: Part B 설명형 시각화 (`site/story.png`는 정적 사본)

## 대시보드 사용법
- 차트 위 **Indicator** 드롭다운: 지표 5개 전환 (아동사망률, 기대수명, 출산율, DTP3 접종률, 보건지출)
- 차트 위 **Year** 드롭다운: 관측연도 전환 (2000–2020, 5년 간격)
- ② 막대 클릭: 지역 강조 (shift-클릭으로 여러 지역 선택)
- ① 점 클릭: ③에 해당 국가 추세 표시 (shift-클릭으로 추가)
- 더블클릭: 해당 차트의 선택 초기화
- 점에 마우스를 올리면 tooltip으로 상세 값 표시

## 데이터 출처
- Gapminder: 수업 제공 `gapminder_2000_2020.csv`
- World Bank: 국가 목록(소득그룹), WDI 보건지출 `SH.XPD.CHEX.GD.ZS`
- WHO GHO: DTP3 접종률 `WHS4_100`

API 응답 원본은 `data/raw/`에 저장되어 있다. `prep.py`는 이 저장본을 쓰고, 파일이 없을 때만 API에서 다시 받는다.

## 재현
```bash
python3 -m venv .venv && .venv/bin/pip install altair pandas vl-convert-python
.venv/bin/python prep.py && .venv/bin/python viz.py
```

## 파일
| 파일 | 내용 |
|---|---|
| `data/gapminder_2000_2020.csv` | 수업 제공 원자료 |
| `data/raw/*.json` | World Bank, WHO API 원본 응답 |
| `data/clean.csv`, `data/prep_log.txt` | 결합·정제 결과와 검증 로그 |
| `prep.py` | 수집, 점검, 조인 검증 |
| `viz.py` | Part A, Part B 생성 |
