# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# Scotland-Housing-Stock-by-Tenure Stock by Tenure and Stock by tenure by LA

# +
from gssutils import *

scraper = Scraper('https://www2.gov.scot/Topics/Statistics/Browse/Housing-Regeneration/HSfS/KeyInfoTables')
scraper
# -

tabs = scraper.distribution().as_databaker()

tab = next(t for t in tabs if t.name=='Tbl Stock by Tenure')
cell = tab.filter(contains_string('Estimated stock'))
year = cell.fill(DOWN).is_not_blank().is_not_whitespace()
tenure =  cell.shift(0,2).fill(RIGHT).is_not_blank().is_not_whitespace() | \
            cell.shift(0,3).fill(RIGHT).is_not_blank().is_not_whitespace()
observations = tenure.fill(DOWN).is_not_blank().is_not_whitespace().is_number()

Dimensions = [
            HDim(year,'Year',DIRECTLY,LEFT),
            HDim(tenure,'Tenure',DIRECTLY,ABOVE),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit', 'dwellings-thousands')
            ]
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
table = c1.topandas()

tidy = pd.DataFrame()

table['Tenure'] = table['Tenure'].map(
    lambda x: {
        'Total number of dwellings (000s)' : 'total', 
        'Owner occupied' : 'privately-owned-dwellings/owner-occupied',
       'Rented privately or with a job/business (note this includes households living rent-free) 3' : 'privately-owned-dwellings/rented-privately-or-with-a-job-business',
       'From housing associations 4' : 'socially-rented-dwellings/from-housing-associations',
       'From local authorities, New Towns, Scottish Homes' : 'socially-rented-dwellings/from-local-authorities-new-towns-scottish-homes',
       'Total number of occupied dwellings (000s)' : 'occupied',
       'Total number of vacant dwellings (000s)' : 'all-vacants',
       'Total number occupied dwellings' : 'privately-owned-dwellings/occupied',
       'Vacant private dwellings and second homes': 'privately-owned-dwellings/vacant-private-dwellings-and-second-homes'
        }.get(x, x))

table['Year'] = table['Year'].str.strip()

table['Period'] = table['Year'].astype(str).str[-4:] + ' ' +  table['Year'].astype(str).str[:3]

# +
import re
YEAR_RE = re.compile(r'[0-9]{4}')
YEAR_MONTH_RE = re.compile(r'([0-9]{4})\s+(JAN|FEB|Mar|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|Dec)')
YEAR_QUARTER_RE = re.compile(r'([0-9]{4})\s+(Q[1-4])')

class Re(object):
  def __init__(self):
    self.last_match = None
  def fullmatch(self,pattern,text):
    self.last_match = re.fullmatch(pattern,text)
    return self.last_match

def time2period(t):
    gre = Re()
    if gre.fullmatch(YEAR_RE, t):
        return f"year/{t}"
    elif gre.fullmatch(YEAR_MONTH_RE, t):
        year, month = gre.last_match.groups()
        month_num = {'JAN': '01', 'FEB': '02', 'Mar': '03', 'APR': '04', 'MAY': '05', 'JUN': '06',
                     'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'Dec': '12'}.get(month)
        return f"month/{year}-{month_num}"
    elif gre.fullmatch(YEAR_QUARTER_RE, t):
        year, quarter = gre.last_match.groups()
        return f"quarter/{year}-{quarter}"
    else:
        print(f"no match for {t}")

table['Period'] = table['Period'].apply(time2period)
# -

import numpy as np
table['OBS'].replace('', np.nan, inplace=True)
table.dropna(subset=['OBS'], inplace=True)
table.rename(columns={'OBS': 'Value'}, inplace=True)
table['Value'] = table['Value'].astype(int)

table['Geography'] = 'S92000003'

table = table[['Period','Geography','Tenure','Measure Type','Value','Unit']]

tidy = pd.concat([tidy , table])

tab1 = next(t for t in tabs if t.name == 'Tbl Stock by tenure by LA')
cell1 = tab1.filter(contains_string('Estimated stock'))
geo = cell1.fill(DOWN).is_not_blank().is_not_whitespace()
tenure1 =  cell1.shift(0,1).fill(RIGHT).is_not_blank().is_not_whitespace() | \
            cell1.shift(0,2).fill(RIGHT).is_not_blank().is_not_whitespace()
observations1 = tenure1.fill(DOWN).is_not_blank().is_not_whitespace().is_number()

Dimensions1 = [
            HDim(geo,'Geography',DIRECTLY,LEFT),
            HDim(tenure1,'Tenure',DIRECTLY,ABOVE),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit', 'dwellings-thousands')
            ]
c2 = ConversionSegment(observations1, Dimensions1, processTIMEUNIT=True)

table1 = c2.topandas()

table1['Tenure'] = table1['Tenure'].map(
    lambda x: {
        'Total number of dwellings (000s)' : 'total', 
        'Owner occupied' : 'privately-owned-dwellings/owner-occupied',
       'Rented privately or with a job/business 3' : 'privately-owned-dwellings/rented-privately-or-with-a-job-business',
       'From housing associations 4' : 'socially-rented-dwellings/from-housing-associations',
       'From local authorities, New Towns, Scottish Homes' : 'socially-rented-dwellings/from-local-authorities-new-towns-scottish-homes',
       'Total number of occupied dwellings (000s)' : 'occupied',
       'Total number of vacant dwellings (000s)' : 'all-vacants',
       'Total number occupied dwellings' : 'privately-owned-dwellings/occupied',
       'Vacant private dwellings and second homes': 'privately-owned-dwellings/vacant-private-dwellings-and-second-homes'
        }.get(x, x))

table1['Period'] = 'month/' + str(cell1)[-7:-3] + '-03'

import numpy as np
table1['OBS'].replace('', np.nan, inplace=True)
table1.dropna(subset=['OBS'], inplace=True)
table1.rename(columns={'OBS': 'Value'}, inplace=True)
table1['Value'] = table1['Value'].astype(int)

scotland_gss_codes = pd.read_csv('scotland-gss.csv', index_col='Area')
table1['Geography'] = table1['Geography'].map(
    lambda x: scotland_gss_codes.loc[x]['Code']
)

table1 = table1[['Period','Geography','Tenure','Measure Type','Value','Unit']]

tidy = pd.concat([tidy , table1])

out = Path('out')
out.mkdir(exist_ok=True)
tidy.drop_duplicates().to_csv(out / 'observations.csv', index = False)

# +
scraper.dataset.family = 'housing'
scraper.dataset.theme = THEME['housing-planning-local-services']
with open(out / 'dataset.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
    
schema = CSVWSchema('https://ons-opendata.github.io/ref_housing/')
schema.create(out / 'observations.csv', out / 'observations.csv-schema.json')
# -

tidy


