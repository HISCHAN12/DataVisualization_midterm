"""Join the course Gapminder file with World Bank and WHO data -> data/clean.csv (+ data/prep_log.txt)."""
import json
import urllib.request
from pathlib import Path

import pandas as pd

RAW = Path('data/raw')
log = []


def fetch_json(url, name):
    # Raw API responses are cached once and reused, so reruns give the same data.
    path = RAW / name
    if not path.exists():
        path.write_bytes(urllib.request.urlopen(url, timeout=60).read())
    return json.loads(path.read_text(encoding='utf-8'))


# 1. Gapminder (course file) — the spine: 195 countries x 5 observation years
gm = pd.read_csv('data/gapminder_2000_2020.csv')
assert not gm.duplicated(['country_code', 'year']).any(), 'duplicate country-year in Gapminder'
assert sorted(gm['year'].unique()) == [2000, 2005, 2010, 2015, 2020], 'unexpected years'
assert (gm.groupby('country_code')['region'].nunique() == 1).all(), 'country changes region'
gm['country'] = gm['country'].str.strip()
gm['region'] = gm['region'].str.strip()
gm['iso3'] = gm['country_code'].str.upper()  # Gapminder uses lowercase ISO3; WB and WHO use uppercase
log.append(f'Gapminder: {len(gm)} rows, {gm.iso3.nunique()} countries, years {sorted(gm.year.unique().tolist())}')

# 2. World Bank country list: income group; drop aggregates such as "World" or "High income"
wb_raw = fetch_json('https://api.worldbank.org/v2/country?format=json&per_page=400', 'wb_countries.json')[1]
wb = pd.DataFrame({'iso3': m['id'], 'wb_region': m['region']['value'].strip(),
                   'income_group': m['incomeLevel']['value']} for m in wb_raw)
n_agg = (wb.wb_region == 'Aggregates').sum()
wb = wb[wb.wb_region != 'Aggregates'].drop(columns='wb_region')
wb['income_group'] = wb['income_group'].replace({'Not classified': pd.NA})
assert wb.iso3.is_unique
log.append(f'World Bank country list: {len(wb_raw)} entries, {n_agg} aggregates removed, {len(wb)} countries kept')

# 3. World Bank WDI: current health expenditure (% of GDP), SH.XPD.CHEX.GD.ZS
he_raw = fetch_json('https://api.worldbank.org/v2/country/all/indicator/SH.XPD.CHEX.GD.ZS'
                    '?format=json&per_page=20000&date=2000:2020', 'wb_health_exp.json')[1]
he = pd.DataFrame({'iso3': r['countryiso3code'], 'year': int(r['date']), 'health_exp_gdp': r['value']}
                  for r in he_raw).dropna()
he = he[he.iso3.isin(wb.iso3)]  # same aggregate filter as the country list
assert not he.duplicated(['iso3', 'year']).any(), 'duplicate country-year in WB health spending'
assert he.health_exp_gdp.between(0, 100).all(), 'health spending outside 0-100 %'

# 4. WHO GHO: DTP3 immunization coverage among 1-year-olds (%), WHS4_100; countries only
who_raw = fetch_json('https://ghoapi.azureedge.net/api/WHS4_100', 'who_dtp3.json')['value']
dtp = pd.DataFrame({'iso3': r['SpatialDim'], 'year': r['TimeDim'], 'dtp3': r['NumericValue']}
                   for r in who_raw if r['SpatialDimType'] == 'COUNTRY').dropna()
log.append(f'WHO DTP3: {len(who_raw)} records, {len(dtp)} country records kept (regional/global/income rows dropped)')
assert not dtp.duplicated(['iso3', 'year']).any(), 'duplicate country-year in WHO'
assert dtp.dtp3.between(0, 100).all(), 'DTP3 outside 0-100 %'

# 5. Join on (ISO3, year), Gapminder as the spine, and verify the join
clean = (gm.merge(wb, on='iso3', how='left', validate='many_to_one')
           .merge(he, on=['iso3', 'year'], how='left', validate='one_to_one')
           .merge(dtp, on=['iso3', 'year'], how='left', validate='one_to_one'))
assert len(clean) == len(gm), 'join changed row count'
log.append(f'Joined: {len(clean)} rows (same as Gapminder)')
for name, src in [('World Bank list', wb), ('WB health spending', he), ('WHO DTP3', dtp)]:
    missing = sorted(set(gm.country[~gm.iso3.isin(src.iso3)]))
    log.append(f'  Gapminder countries absent from {name}: {len(missing)} {missing}')

# Missing values stay missing (no interpolation); each chart drops only rows it cannot draw.
cols = ['income_per_capita', 'child_mortality', 'life_expectancy', 'fertility_rate',
        'health_exp_gdp', 'dtp3', 'income_group']
log.append('Missing share after join: ' + ', '.join(f'{c} {clean[c].isna().mean():.1%}' for c in cols))

keep = ['iso3', 'country', 'region', 'income_group', 'year', 'population'] + cols[:-1]
clean[keep].to_csv('data/clean.csv', index=False)
Path('data/prep_log.txt').write_text('\n'.join(log) + '\n', encoding='utf-8')
print('\n'.join(log))
