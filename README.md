# Data Visualization Midterm: Child Health Gaps Between Countries (2000–2020)

## Open these first
1. **Part A dashboard (interactive):** https://hischan12.github.io/DataVisualization_midterm/site/dashboard.html
2. **Part B story (fixed view):** https://hischan12.github.io/DataVisualization_midterm/site/story.html
3. **Report:** `report.md` (data, design reasons, limitations, bonus work)

Start page with both links: https://hischan12.github.io/DataVisualization_midterm/

Offline: open `site/dashboard.html` or `site/story.html` in a web browser. An internet connection is needed because the chart library (Vega) loads from a CDN. `site/story.png` is a picture copy of Part B.

## How to use the dashboard
- **Indicator** dropdown (above the charts): switch between 5 indicators (child mortality, life expectancy, fertility rate, DTP3 vaccine coverage, health spending)
- **Year** dropdown (above the charts): switch between 2000, 2005, 2010, 2015 and 2020
- Click a bar in chart 2: highlight that region (shift-click to add regions)
- Click a point in chart 1: show that country's trend in chart 3 (shift-click to add countries)
- Double-click chart 1 or 2: clear its selection
- Hover over a point: see exact values

## Data sources
- Gapminder: class file `gapminder_2000_2020.csv`
- World Bank: country list (income group), WDI health spending `SH.XPD.CHEX.GD.ZS`
- WHO GHO: DTP3 vaccine coverage `WHS4_100`

The original API downloads are saved in `data/raw/`. `prep.py` uses these saved files and downloads again only if a file is missing.

## Rebuild everything
```bash
python3 -m venv .venv && .venv/bin/pip install altair pandas vl-convert-python
.venv/bin/python prep.py && .venv/bin/python viz.py
```

## Files
| File | Contents |
|---|---|
| `data/gapminder_2000_2020.csv` | class data file |
| `data/raw/*.json` | original World Bank and WHO API downloads |
| `data/clean.csv`, `data/prep_log.txt` | joined and cleaned data, and the check log |
| `prep.py` | collect, check and join the data |
| `viz.py` | build Part A and Part B |
| `site/` | the published dashboard, story and story picture |
| `index.html` | start page for GitHub Pages |
