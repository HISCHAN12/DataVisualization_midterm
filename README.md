# 중간과제: 국가 간 아동사망률 격차 (2000–2020)

## 먼저 열 파일
1. `report.md`: 보고서 (데이터, 설계 근거, 한계)
2. `site/dashboard.html`: Part A 탐색형 대시보드. 브라우저로 열기 (인터넷 연결 필요: Vega 라이브러리를 CDN에서 불러옴)
3. `site/story.html`: Part B 설명형 시각화 (`site/story.png`는 정적 사본)

## 대시보드 사용법
- 차트 아래 **Year** 드롭다운: 연도 변경
- ② 막대 클릭: 지역 강조 (shift-클릭으로 여러 지역 선택)
- ① 점 클릭: ③에 해당 국가 추세 표시 (shift-클릭으로 추가)
- 더블클릭: 해당 차트의 선택 초기화
- 점에 마우스를 올리면 tooltip으로 상세 값 표시

## 재현
```bash
python3 -m venv .venv && .venv/bin/pip install altair pandas vl-convert-python
.venv/bin/python prep.py && .venv/bin/python viz.py
```

## 파일
| 파일 | 내용 |
|---|---|
| `data/gapminder_2000_2020.csv` | 수업 제공 원자료 |
| `data/clean.csv`, `data/prep_log.txt` | 전처리 결과와 점검 로그 |
| `prep.py` | 데이터 점검·정제 |
| `viz.py` | Part A, Part B 생성 |
