# Data Visualization Midterm Report: Child Health Gaps Between Countries, 2000–2020

- **Part A (exploratory dashboard):** https://hischan12.github.io/DataVisualization_midterm/site/dashboard.html
- **Part B (explanatory visualization):** https://hischan12.github.io/DataVisualization_midterm/site/story.html (a picture copy is `site/story.png`)
- **Start page:** https://hischan12.github.io/DataVisualization_midterm/
- **Code and data:** https://github.com/HISCHAN12/DataVisualization_midterm
- **Tools:** Python, pandas, Altair 6 (mostly the methods from the Week 1–2 Altair lessons)

---

## 1. Data

### Sources (accessed 2026-10-23; the original downloads are saved in `data/raw/`)

| Source | What I used (code) | Unit | URL |
|---|---|---|---|
| Gapminder (class file `gapminder_2000_2020.csv`) | child mortality, income, life expectancy, fertility rate, population, region | deaths per 1,000 births / $ per day (2017 PPP) / years / births per woman / people | https://www.gapminder.org/data |
| World Bank country list | income group, and which rows are groups (not countries) | category | https://api.worldbank.org/v2/country |
| World Bank WDI | Current health expenditure (SH.XPD.CHEX.GD.ZS) | % of GDP | https://data.worldbank.org/indicator/SH.XPD.CHEX.GD.ZS |
| WHO GHO | DTP3 immunization coverage among 1-year-olds (WHS4_100) | % | https://ghoapi.azureedge.net/api/WHS4_100 |

- **One row** = one country in one year. There are 975 rows.
- **Coverage:** 195 countries, 6 regions (Gapminder's regions), and 5 observation years: 2000, 2005, 2010, 2015, 2020. These are not yearly data; they are 5 snapshots. The World Bank and WHO have yearly data, so I kept only these 5 years.
- **Income unit:** The income column had no unit written on it, so I checked it with real countries. In 2020 the values are USA 96.5, South Korea 61.3, India 6.0 and Monaco 513. If this is "dollars per day", Monaco is about $190,000 per year, which makes sense. If it were "thousand dollars per year", Monaco would be $513,000, which is impossible. So the unit is **dollars per person per day (2017 PPP)**.

The Week 1 notebook says the source of the class file should be checked before serious statistical use. So I only describe and compare; I do not test causes.

### Collecting, cleaning and joining (`prep.py` → `data/clean.csv`, log in `data/prep_log.txt`)

1. **Collecting:** I downloaded the World Bank and WHO data from their official APIs. The raw answers are saved in `data/raw/`. When the code runs again, it uses these saved files, so the result is always the same.
2. **Matching countries:** Each source writes country codes differently. Gapminder uses small letters (`afg`), so I changed them to capital ISO3 codes (`AFG`) and joined the tables on (country code, year). I did not join on country names, because the names are spelled differently in each source (for example "Congo, Dem. Rep.").
3. **Removing groups:** The World Bank list has 296 rows, but 79 of them are groups such as "World", "Sub-Saharan Africa" or "High income", not countries. I removed them, and did the same for the health spending data. In the WHO data I kept only rows marked `COUNTRY`, which removed 286 region, world and income-group rows. If these groups stayed in, the country medians would be wrong.
4. **Checking the join** (every check is an `assert`, so the code stops if one fails):
   - each source has only one row per (country, year)
   - pandas `merge(validate=...)` checks that the join matches rows one-to-one
   - after joining there are still exactly 975 rows, the same as the Gapminder file
   - DTP3 and health spending are between 0 and 100 %
   - Gapminder has exactly 5 years, and each country belongs to only one region
5. **Countries with no match** (written in the log):
   - not in the World Bank list: Holy See
   - no health spending data: Holy See, North Korea
   - no DTP3 data: Holy See, Liechtenstein
6. **Missing values:** I did not fill in missing values with guesses. Each chart only leaves out the rows it cannot draw. Missing shares after the join: income 1.0%, child mortality 0.8%, life expectancy 0.5%, fertility 0.0%, health spending 3.3%, DTP3 1.6%, income group 0.5%.
7. **Filter first, then summarize:** In Part A, the indicator, year and region choices are applied before the medians are calculated (Altair Week 1: "Filter order changes the question").

**What the joined data adds:** With Gapminder alone, I can only find countries that have different child mortality at the same income. With WHO vaccine coverage and World Bank health spending added, the user can switch the indicator and see whether those same countries are also different in vaccines or health spending. The World Bank income group in the tooltip helps the user read Gapminder income. In Part B, WHO vaccine coverage and Gapminder income give context to the main message (see Section 3, "Context").

**What was hard:** The sources write country codes in different ways. The World Bank API mixes countries and groups in one list. The income column had no unit, so I had to work out the unit from real country values.

---

## 2. Part A: Exploratory Dashboard

### Purpose
- **Users:** students and workers who study global health and development
- **Scope:** 195 countries, 2000–2020, 6 regions, 5 indicators (child mortality, life expectancy, fertility rate, DTP3 vaccine coverage, health spending)
- **Example questions users can explore**
  1. Which region had the highest child mortality in 2000, and did the order change by 2020? (change the year, look at chart 2)
  2. Which countries have much higher or lower child mortality than others at the same income? Is their DTP3 coverage also different? (chart 1 and tooltip, then switch the indicator to DTP3)
  3. At a similar income, how different are fertility rates or health spending between countries? (switch the indicator, look at how spread out chart 1 is from top to bottom)
  4. How did one country's vaccine coverage or life expectancy change over 20 years, compared with the median of all countries? (click a country in chart 1, look at chart 3)

### Views and how to use them
| View | Encoding | Interaction | Questions |
|---|---|---|---|
| **Indicator / Year dropdowns (above the charts)** | — | choose 1 of 5 indicators and 1 of 5 years; this changes charts 1–3 and the status text together | all |
| ① Income vs. indicator scatter plot | x = income (log scale), y = chosen indicator, color = region | click a country to add its line to chart 3 (shift-click to add more); tooltip with details, including the World Bank income group | Q2, Q3 |
| ② Median by region bar chart | bar length, sorted from largest to smallest | click a bar to highlight that region in chart 1 (other regions turn gray) | Q1 |
| ③ Trend of selected countries | position on a shared axis (lines and points), country names written at the end of each line | shows only the countries clicked in chart 1; the dashed line is the median of all countries | Q4 |
| Current selection | text | shows the year, how many regions are selected, how many countries have data, and the median | to see what is selected now |

- **Default view:** child mortality, 2020, all regions. Chart 3 already shows 4 very different countries (Nigeria, India, Brazil, South Korea), so the first screen is useful right away (Altair Week 2 p.16, initial `value`).
- **Reset:** double-click chart 1 or 2 to clear its selection (`clear='dblclick'`). This is written in the chart subtitles.
- **Titles and y-axis titles:** the chosen indicator and its unit appear in the chart titles and the y-axis titles (`alt.expr`). Altair axis titles cannot read a parameter, so I drew the y-axis title as rotated text. The user always knows what is shown and in which unit.
- **Instructions on the page:** the top of the dashboard page explains who it is for, what data it covers, how to use it, and example questions. Someone who opens only the URL can use it without reading this report.

### Design reasons (course concepts)
- **Controls on top:** Altair puts the dropdowns below the charts, where users may not see them. People do not memorize a new layout (postattentive vision), so the controls must be easy to see right away. I used CSS (`flex-direction: column-reverse`) to move them above the charts.
- **Cleveland & McGill ranking:** People read position on a shared scale and length most accurately. So every value that needs exact comparison uses position (charts 1 and 3) or length (chart 2). I did not show population as bubble size, because people judge area poorly (area grows with the square of the radius). Population is in the tooltip instead.
- **Scales:** Income goes from about $1 to $530 per day, so I used a log scale, which spreads out "times bigger" differences evenly (Altair Week 1 Gapminder example). The y-axis must work for all 5 indicators. Some of them (percentages, fertility) do not suit a log scale, so the y-axis is linear (`zero=False`). Low child mortality values look squeezed together, so the tooltip gives the exact numbers.
- **Highlight vs. filter** (Altair Week 2 p.19–20): Choosing a region **highlights** it in chart 1, so the other countries stay as gray context. The status text **filters** to the selected region to calculate its numbers. Choosing a country **filters** chart 3.
- **Pre-attentive pop-out and similarity theory:** Unselected marks all become the same light gray (background items look alike). Selected countries get a black outline, so they look very different from the background and pop out.
- **Feature hierarchy:** Color is the strongest channel, so it shows the main variable, region. The less important information, whether a country is selected, uses an outline, so the two do not get in each other's way.
- **Change blindness:** Users may not notice that something changed. So the chart titles and the "Current selection" text say clearly what is shown now (Altair Week 2 dashboard pattern).
- **Meaning of the reference line** (Altair Week 2 p.34): The dashed line in chart 3 is the median of all countries for the chosen indicator. It does not move when you click countries. The subtitle says this.
- **Consistent colors, no color clash:** Region colors are the same in charts 1 and 2. In chart 3 the country lines are black with names written next to them, not colored. If countries had colors, they could look like region colors (for example India orange = South Asia orange). This also removes the need to look back and forth at a legend.

---

## 3. Part B: Explanatory Visualization

### Key message
> **From 2000 to 2020, child mortality in Sub-Saharan Africa fell so much that its absolute gap with Europe & Central Asia shrank by more than half. But the relative gap did not shrink: it is still 11–14 times higher.**

- **Audience:** general readers interested in development and health policy
- **Why it matters:** People often say "the gap got smaller". That is true if you subtract (absolute gap) but not if you divide (relative gap). How you measure a gap changes how you judge progress.

### Charts and reading order
| Order | Chart | Evidence |
|---|---|---|
| ① | Median child mortality by region over time (linear axis starting at 0) | It fell in every region. The biggest drop was in Sub-Saharan Africa (139 → 59 per 1,000, −80). |
| ② | Absolute gap bars (Sub-Saharan Africa minus Europe) | 129 → 55, less than half |
| ③ | Relative gap lines (Sub-Saharan Africa divided by Europe) | Country median: 14.6 → 14.4 times, almost no change. Population-weighted: 9.1 → 11.5 times, it even grew. A reference line marks "1× = no gap". |

**Why this happens:** From 2000 to 2020 child mortality fell by 58% in Sub-Saharan Africa and by 57% in Europe & Central Asia, almost the same rate. When two numbers fall by the same percentage, the bigger number loses many more deaths, so the absolute gap shrinks while the ratio stays the same.

### Design reasons
- **Titles that state the finding:** The main title and every chart title is a sentence that says the result (Altair Week 2 p.47, "Evening flights have the highest…" pattern).
- **One accent color, gray for the rest:** Only the two regions being compared have colors (red and teal). The other four regions are gray but still shown, so nothing is hidden (no cherry-picking), and the two main lines pop out.
- **Direct labels instead of a legend:** Names and key numbers are written right next to the lines, so readers do not have to look back and forth at a legend.
- **Avoiding the curvature trap** (Graphical Perception): Readers are bad at judging the distance between two lines by eye. So I calculated the gap and drew it directly in charts ② and ③.
- **Honest axes:** The bars (②) and the ratio (③) start at 0. With the ratio axis from 0 to 18, "almost flat" really looks flat, with no exaggeration.
- **Feature hierarchy:** In ③, the main measure (country median) is a solid red line, and the second measure (population-weighted) is a gray dashed line.
- **Fixed view:** Part B has no interaction. The message and all the evidence are visible without clicking anything.
- **No chartjunk:** I removed grid lines and borders (`configure_view(stroke=None)`, `grid=False`).
- **The code checks the claim:** `assert` lines in `viz.py` check the title's claims with the data (the absolute gap is less than half; the ratio did not shrink). If the data changed and the claim became false, the build would stop.

### Context (from the joined data)
Two lines under the main title give context (region medians, 2000 → 2020):
- **Vaccine gap (WHO DTP3):** The difference between Europe & Central Asia and Sub-Saharan Africa narrowed from 32 to 11 percentage points (96% vs 64% → 94% vs 83%).
- **Income gap (Gapminder):** Europe's income lead grew from 6.6 times to 9.6 times.

I only say that these changes happened at the same time. I do not claim which one keeps the relative gap large. This leaves the reader with a fair next question: "The basic vaccine gap closed, so why is the relative death gap still the same?" The numbers are calculated by `viz.py` from the same data, so the report and the chart always match.

### Limitations
- **Type of summary:** Each region is represented by the median country. Countries inside a region are very different (you can see this in Part A), and the ratio is 9–14 times depending on whether you weight by population. That is why both are shown.
- **Number of countries:** Regions have different numbers of countries (from 8 in South Asia to 54 in Europe & Central Asia).
- **Only 5 years:** The data has only 5 observation years; the lines between the points are drawn in, not measured.
- **No causes:** This comparison does not show why child mortality fell (income, health spending, vaccines, or something else).
- **Source check:** I did not compare the class file's values and versions with Gapminder's original data.

---

## 4. Bonus Work

| Item | Status |
|---|---|
| Part A online | **Submitted:** https://hischan12.github.io/DataVisualization_midterm/site/dashboard.html |
| Part B online | **Submitted:** https://hischan12.github.io/DataVisualization_midterm/site/story.html |
| Data collection and integration | **Submitted:** 4 datasets from 3 organizations (Gapminder, World Bank, WHO), joined on country code and year and checked (Section 1). The joined data is used for the 5 indicators in Part A and the context in Part B. |
