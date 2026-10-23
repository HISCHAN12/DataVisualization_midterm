"""Build Part A (site/dashboard.html) and Part B (site/story.html, site/story.png) from data/clean.csv."""
import altair as alt
import pandas as pd

gap = pd.read_csv('data/clean.csv')
YEARS = [2000, 2005, 2010, 2015, 2020]
REGIONS = ['Sub-Saharan Africa', 'South Asia', 'East Asia & Pacific',
           'Middle East & North Africa', 'Americas', 'Europe & Central Asia']
region_color = alt.Color('region:N', title='Region', sort=REGIONS,
                         scale=alt.Scale(domain=REGIONS, range=['#C7523B', '#E28A45', '#7C6AA5',
                                                                '#B8A13A', '#5B8E3E', '#187D91']))
CM = 'Child mortality (deaths under 5 per 1,000 births)'

# ---------------- Part A: exploratory dashboard ----------------
plot = gap.dropna(subset=['income_per_capita', 'child_mortality'])

year = alt.param(name='year_sel', value=2020,
                 bind=alt.binding_select(options=YEARS, name='Year: '))
region_pick = alt.selection_point(name='region_pick', fields=['region'], clear='dblclick')
country_pick = alt.selection_point(
    name='country_pick', fields=['country'], empty=False, clear='dblclick',
    value=[{'country': c} for c in ['Nigeria', 'India', 'Brazil', 'South Korea']])

eligible = alt.Chart(plot).transform_filter(alt.datum.year == year)

scatter = eligible.mark_circle(size=70, opacity=0.8).encode(
    x=alt.X('income_per_capita:Q', scale=alt.Scale(type='log', domain=[0.5, 600]),
            title='Income per person (thousand $, PPP, log scale)'),
    y=alt.Y('child_mortality:Q', scale=alt.Scale(type='log', domain=[1.5, 250]),
            title=CM + ', log scale'),
    color=alt.when(region_pick).then(region_color).otherwise(alt.value('#DDDDDD')),
    stroke=alt.when(country_pick).then(alt.value('black')).otherwise(alt.value(None)),
    strokeWidth=alt.when(country_pick).then(alt.value(2)).otherwise(alt.value(0)),
    order=alt.when(region_pick).then(alt.value(1)).otherwise(alt.value(0)),
    tooltip=[alt.Tooltip('country:N', title='Country'), alt.Tooltip('region:N', title='Region'),
             alt.Tooltip('year:O', title='Year'),
             alt.Tooltip('income_per_capita:Q', title='Income (k$ PPP)', format=',.1f'),
             alt.Tooltip('child_mortality:Q', title='Child mortality (/1,000)', format='.1f'),
             alt.Tooltip('life_expectancy:Q', title='Life expectancy (yrs)', format='.1f'),
             alt.Tooltip('population:Q', title='Population', format=',.0f')]
).add_params(country_pick).properties(
    width=430, height=330,
    title=alt.Title('1. Income and child mortality by country',
                    subtitle='Click a country to show its trend in chart 3 (shift-click to add).'))

region_bars = eligible.mark_bar().encode(
    y=alt.Y('region:N', sort='-x', title=None),
    x=alt.X('median(child_mortality):Q', title='Median child mortality (per 1,000)',
            scale=alt.Scale(domain=[0, 150])),
    color=alt.when(region_pick).then(region_color).otherwise(alt.value('#DDDDDD')),
    tooltip=[alt.Tooltip('region:N', title='Region'),
             alt.Tooltip('median(child_mortality):Q', title='Median (/1,000)', format='.1f'),
             alt.Tooltip('count():Q', title='Countries')]
).add_params(region_pick).properties(
    width=330, height=330,
    title=alt.Title('2. Median by region (country median)',
                    subtitle='Click a bar to highlight a region (shift-click to add).'))

trend_base = alt.Chart(gap.dropna(subset=['child_mortality']))
trend_lines = trend_base.transform_filter(country_pick).mark_line(point=True).encode(
    x=alt.X('year:O', title='Observation year (5-year steps)', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('child_mortality:Q', title=CM, scale=alt.Scale(domain=[0, 230])),
    color=alt.Color('country:N', title='Selected country'),
    tooltip=[alt.Tooltip('country:N', title='Country'), alt.Tooltip('year:O', title='Year'),
             alt.Tooltip('child_mortality:Q', title='Child mortality (/1,000)', format='.1f')])
# Full-data reference: does not react to any selection.
world_median = trend_base.mark_line(color='#888888', strokeDash=[4, 4]).encode(
    x='year:O', y='median(child_mortality):Q')
world_label = trend_base.transform_filter(alt.datum.year == 2020).mark_text(
    align='left', dx=6, color='#666666').encode(
    x='year:O', y='median(child_mortality):Q', text=alt.value('All-country median'))
trend = (world_median + world_label + trend_lines).properties(
    width=430, height=260,
    title=alt.Title('3. Trend of selected countries, 2000–2020',
                    subtitle='Dashed: median of all countries. Lines between points are interpolated.'))

status = eligible.transform_filter(region_pick).transform_aggregate(
    n='count()', med='median(child_mortality)', regions='distinct(region)'
).transform_calculate(
    line1="'Year ' + year_sel + ' · ' + (datum.regions == 6 ? 'all regions' : datum.regions + ' region(s) selected')",
    line2="format(datum.n, ',.0f') + ' countries · median ' + format(datum.med, '.1f') + ' per 1,000'"
).mark_text(fontSize=17, align='left').encode(x=alt.value(0), y=alt.value(40), text='line1:N')
status2 = status.encode(y=alt.value(75), text='line2:N')
status_box = (status + status2).properties(
    width=330, height=260,
    title=alt.Title('Current selection',
                    subtitle=['Double-click chart 1 or 2 to clear its selection.',
                              'Blank? Clear the region selection.']))

dashboard = alt.vconcat(
    scatter | region_bars,
    trend | status_box
).add_params(year).resolve_scale(color='independent').properties(
    title=alt.Title('Child mortality explorer: 195 countries, 2000–2020',
                    subtitle=['Data: Gapminder (course file gapminder_2000_2020.csv). Choose a year below the charts.',
                              'Questions: Which regions lag? Which countries do better than their income suggests? How fast did a country improve?'])
).configure_view(stroke=None)
dashboard.save('site/dashboard.html')

# ---------------- Part B: explanatory story ----------------
cm = gap.dropna(subset=['child_mortality'])
summary = cm.groupby(['region', 'year'], as_index=False).agg(
    median=('child_mortality', 'median'), n=('child_mortality', 'size'))
wide = summary.pivot(index='year', columns='region', values='median')
pop = cm.dropna(subset=['population']).assign(w=lambda d: d.child_mortality * d.population)
pop = pop.groupby(['region', 'year']).agg(w=('w', 'sum'), p=('population', 'sum'))
pop = (pop.w / pop.p).unstack('region')

SSA, EUR = 'Sub-Saharan Africa', 'Europe & Central Asia'
gaps = pd.DataFrame({'year': YEARS,
                     'abs_gap': (wide[SSA] - wide[EUR]).values,
                     'ratio_median': (wide[SSA] / wide[EUR]).values,
                     'ratio_pop': (pop[SSA] / pop[EUR]).values})
# Self-check: the claim in the title must hold in the data.
assert gaps.abs_gap.iloc[-1] < gaps.abs_gap.iloc[0] / 2
assert gaps.ratio_median.iloc[-1] > 0.95 * gaps.ratio_median.iloc[0]
assert gaps.ratio_pop.iloc[-1] > gaps.ratio_pop.iloc[0]
print(gaps.round(2).to_string(index=False))

ACCENT = {SSA: '#C7523B', EUR: '#187D91'}
# Americas and MENA end within 0.3 of each other in 2020, so they share one label.
summary['label'] = summary.region.replace({'Americas': 'Americas · Middle East & N. Africa',
                                           'Middle East & North Africa': ''})
line_color = alt.Color('region:N', legend=None,
                       scale=alt.Scale(domain=REGIONS,
                                       range=[ACCENT.get(r, '#BECBD0') for r in REGIONS]))
lines_base = alt.Chart(summary).encode(
    x=alt.X('year:O', title=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y('median:Q', title='Deaths under 5 per 1,000 births', scale=alt.Scale(domain=[0, 150])),
    color=line_color)
end_labels = lines_base.transform_filter(alt.datum.year == 2020).mark_text(
    align='left', dx=8, fontSize=12).encode(
    text='label:N')
point_labels = lines_base.transform_filter(alt.datum.region == SSA).mark_text(dy=-10, fontSize=11).encode(
    text=alt.Text('median:Q', format='.0f'))
chart1 = (lines_base.mark_line(point=True, strokeWidth=2.5) + end_labels + point_labels).properties(
    width=520, height=300,
    title=alt.Title('① Child mortality fell in every region; the biggest drop was in Sub-Saharan Africa',
                    subtitle=['Median of countries in each region; 193 countries with data.',
                              'Sub-Saharan Africa: 139 → 59 per 1,000 (−80). Europe & Central Asia: 9.5 → 4.1.'],
                    anchor='start'))

gap_bars = alt.Chart(gaps).mark_bar(color='#C7523B', size=34).encode(
    x=alt.X('year:O', title=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y('abs_gap:Q', title='Gap (deaths per 1,000)', scale=alt.Scale(domain=[0, 140])))
gap_text = gap_bars.mark_text(dy=-8, color='#333333').encode(text=alt.Text('abs_gap:Q', format='.0f'))
chart2 = (gap_bars + gap_text).properties(
    width=300, height=260,
    title=alt.Title('② The absolute gap more than halved',
                    subtitle='Sub-Saharan Africa minus Europe & Central Asia (medians)', anchor='start'))

ratio_long = gaps.melt('year', ['ratio_median', 'ratio_pop'], var_name='measure', value_name='ratio')
ratio_long['measure'] = ratio_long.measure.map({'ratio_median': 'Country median',
                                                'ratio_pop': 'Population-weighted'})
ratio_base = alt.Chart(ratio_long).encode(
    x=alt.X('year:O', title=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y('ratio:Q', title='Ratio (times higher)', scale=alt.Scale(domain=[0, 18])),
    color=alt.Color('measure:N', scale=alt.Scale(domain=['Country median', 'Population-weighted'],
                                                 range=['#C7523B', '#888888']), legend=None),
    strokeDash=alt.StrokeDash('measure:N', scale=alt.Scale(domain=['Country median', 'Population-weighted'],
                                                           range=[[1, 0], [5, 4]]), legend=None))
ratio_lines = ratio_base.mark_line(point=True, strokeWidth=2.5)
ratio_text = ratio_base.transform_filter(
    (alt.datum.year == 2000) | (alt.datum.year == 2020)).mark_text(dy=-10).encode(
    text=alt.Text('ratio:Q', format='.1f'))
ratio_names = ratio_base.transform_filter(alt.datum.year == 2020).mark_text(
    align='left', dx=10, dy=6).encode(text='measure:N')
parity = alt.Chart(pd.DataFrame({'y': [1]})).mark_rule(color='#999999', strokeDash=[2, 2]).encode(y='y:Q')
parity_text = alt.Chart(pd.DataFrame({'y': [1], 't': ['1× = no gap']})).mark_text(
    align='left', dy=-6, x=4, color='#777777').encode(y='y:Q', text='t:N')
chart3 = (parity + parity_text + ratio_lines + ratio_text + ratio_names).properties(
    width=300, height=260,
    title=alt.Title('③ …but the relative gap did not shrink',
                    subtitle='Sub-Saharan Africa ÷ Europe & Central Asia', anchor='start'))

story = alt.vconcat(chart1, alt.hconcat(chart2, chart3, spacing=110), spacing=40).properties(
    title=alt.Title(
        'Child mortality fell fast in Sub-Saharan Africa, yet it is still 11–14 times Europe’s',
        subtitle=['Data: Gapminder, course file gapminder_2000_2020.csv; five observation years; 193 countries with child mortality data.',
                  'Descriptive comparison of regional summaries. It does not show causes, and country-level variation within regions is large.'],
        fontSize=18, anchor='start', offset=16)
).configure_view(stroke=None).configure_axis(grid=False, labelFontSize=12, titleFontSize=12)
story.save('site/story.html')
story.save('site/story.png', scale_factor=2)
