import numpy as np
import pandas as pd
import eurostat
import pycountry
import seaborn as sns

df = eurostat.get_data_df('demo_r_mwk_20')
df.columns = df.columns.str.replace('\\', '_',regex=False)
df = df[df.age != 'UNK']
df['age'].replace(['Y20-39', 'Y40-59', 'Y60-79', 'Y_GE80', 'Y_LT20'],['20-39', '40-59', '60-79', '80+', '0-20'], inplace=True)
df2=pd.melt(df,id_vars=['age','sex','unit','geo_time'],var_name='yearweek', value_name='deaths')
df_clean = df2.drop(columns = ['unit'])
df_clean[['year','week']] = df_clean.yearweek.str.split("W",expand=True)
df_clean['week'] = df_clean.week.str.extract('(\d+)')
df_clean['year'] = df_clean.year.str.extract('(\d+)')
df_clean['geo_time'] = df_clean['geo_time'].replace("UK", "GB")
df_clean['geo_time'] = df_clean['geo_time'].replace("EL", "GR")
countries = {}
for country in pycountry.countries:
    countries[country.alpha_2] = country.name
df_clean['country'] = [countries.get(country, 'Unknown code') for country in df_clean.geo_time]
df_clean = df_clean[['country','sex','age','yearweek','year','week','deaths']]
#remove this line to get the full time period
df_clean['covid_year']=df_clean['year'] >= '2020'
df_clean.loc[df_clean['covid_year'] == False, 'covid_year'] = '2000-2019 +/- SD'
df_clean.loc[df_clean['covid_year'] == True, 'covid_year'] = df_clean['year']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']

g = sns.FacetGrid(df_clean.query("sex == 'T'"), col="age", hue="covid_year", row='country', aspect=2,sharey=False)
g.map(sns.lineplot, 'week', 'deaths', alpha=.7, estimator='mean', ci='sd')
g.set(xlabel="month", ylabel = "deaths per week", xticks=np.arange(1, 53,(53/12) ), xticklabels=months)
g.add_legend(title = '')
for suffix in 'png svg'.split():
    g.savefig('by_country_age.'+suffix, dpi=200, bbox_inches='tight', facecolor='white')

g = sns.FacetGrid(df_clean.query("age == 'TOTAL'"), col="sex", hue="covid_year", row='country', aspect=2,sharey=False)
g.map(sns.lineplot, 'week', 'deaths', alpha=.7, estimator='mean', ci='sd')
g.set(xlabel="month", ylabel = "deaths per week", xticks=np.arange(1, 53,(53/12) ), xticklabels=months)
g.add_legend(title = '')
for suffix in 'png svg'.split():
    g.savefig('by_country_sex.'+suffix, dpi=200, bbox_inches='tight', facecolor='white')

df_total=df_clean.query("age == 'TOTAL' & sex == 'T'").groupby(['yearweek', 'year', 'week', 'covid_year'], as_index=False)['deaths'].sum()
df_total

g = sns.FacetGrid(df_total, hue="covid_year", aspect=2,sharey=False)
g.map(sns.lineplot, 'week', 'deaths', alpha=.7, estimator='mean', ci='sd')
g.set(xlabel="month", ylabel = "deaths per week", xticks=np.arange(1, 53,(53/12) ), xticklabels=months)
g.add_legend(title = '')
for suffix in 'png svg'.split():
    g.savefig('total.'+suffix, dpi=200, bbox_inches='tight', facecolor='white')