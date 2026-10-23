"""Audit and clean the course-supplied gapminder_2000_2020.csv -> data/clean.csv."""
import pandas as pd

raw = pd.read_csv('data/gapminder_2000_2020.csv')

# Data audit (Week 1 section 0 style): check the unit of observation before charting.
assert not raw.duplicated(['country_code', 'year']).any(), 'duplicate country-year rows'
assert sorted(raw['year'].unique()) == [2000, 2005, 2010, 2015, 2020], 'unexpected years'
assert (raw.groupby('country_code')['region'].nunique() == 1).all(), 'country changes region'

clean = raw.copy()
clean['country'] = clean['country'].str.strip()
clean['region'] = clean['region'].str.strip()
# Missing values stay missing; each chart drops only the rows it cannot draw.
clean.to_csv('data/clean.csv', index=False)

print(f'rows {len(clean)}, countries {clean.country_code.nunique()}, years {sorted(clean.year.unique().tolist())}')
print('countries per region:', clean.groupby('region').country_code.nunique().to_dict())
print('missing values:', clean.isna().sum()[lambda s: s > 0].to_dict())
print('no child_mortality:', sorted(clean.loc[clean.child_mortality.isna(), 'country'].unique()))
print('no income:', sorted(clean.loc[clean.income_per_capita.isna(), 'country'].unique()))
