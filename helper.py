import numpy as np
import pandas as pd


def fetch_medal_tally(df, year, country):
    # Remove duplicate medal entries
    medal_df = df.drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
    )
    flag = 0

    # Apply filters based on year and country
    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
    elif year == 'Overall' and country != 'Overall':
        flag = 1
        temp_df = medal_df[medal_df['region'] == country]
    elif year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
    else:
        temp_df = medal_df[(medal_df['Year'] == int(year)) & (medal_df['region'] == country)]

    # Group and aggregate medal counts
    if flag == 1:
        x = (
            temp_df.groupby('Year')
            .sum(numeric_only=True)[['Gold', 'Silver', 'Bronze']]
            .sort_values('Year')
            .reset_index()
        )
    else:
        x = (
            temp_df.groupby('region')
            .sum(numeric_only=True)[['Gold', 'Silver', 'Bronze']]
            .sort_values('Gold', ascending=False)
            .reset_index()
        )

    # Compute total medals
    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']

    # Ensure integer columns
    for col in ['Gold', 'Silver', 'Bronze', 'total']:
        x[col] = x[col].astype(int)

    return x


def country_year_list(df):
    years = sorted(df['Year'].unique().tolist())
    years.insert(0, 'Overall')

    countries = sorted(np.unique(df['region'].dropna().values).tolist())
    countries.insert(0, 'Overall')

    return years, countries


def data_over_time(df, col):
    # Clean version — avoids KeyError
    temp_df = df.drop_duplicates(['Year', col])
    over_time = temp_df.groupby('Year').size().reset_index(name=col)
    return over_time


def most_successful(df, sport):
    temp_df = df.dropna(subset=['Medal'])

    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    # Count medals per athlete
    medal_count = temp_df['Name'].value_counts().reset_index()
    medal_count.columns = ['Name', 'Medals']

    # Merge to get additional info
    merged_df = medal_count.merge(df[['Name', 'Sport', 'region']], on='Name', how='left').drop_duplicates('Name')

    # Keep top 15 athletes
    merged_df = merged_df.head(15)

    return merged_df


def yearwise_medal_tally(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df.drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
    )

    country_df = temp_df[temp_df['region'] == country]
    final_df = country_df.groupby('Year').count()['Medal'].reset_index()
    return final_df


def country_event_heatmap(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df.drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal']
    )

    country_df = temp_df[temp_df['region'] == country]

    pt = country_df.pivot_table(
        index='Sport', columns='Year', values='Medal', aggfunc='count'
    ).fillna(0)

    return pt


def most_successful_countrywise(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df[temp_df['region'] == country]

    medal_count = temp_df['Name'].value_counts().reset_index()
    medal_count.columns = ['Name', 'Medals']

    merged_df = medal_count.merge(df[['Name', 'Sport']], on='Name', how='left').drop_duplicates('Name')
    merged_df = merged_df.head(10)

    return merged_df


def weight_v_height(df, sport):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    athlete_df['Medal'] = athlete_df['Medal'].fillna('No Medal')

    if sport != 'Overall':
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        return temp_df
    else:
        return athlete_df


def men_vs_women(df):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()

    final = men.merge(women, on='Year', how='left')
    final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)
    final.fillna(0, inplace=True)

    return final
