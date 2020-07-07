import requests
from html import unescape
import re
import datetime
import numpy as np
import pandas as pd
import unicodedata


def get_data(section):
    """
    Makes GET request to the respective [section] of the eVM,
    fixes html encodings and returns the html
    """

    url = f"https://evm.min-saude.pt/table?t={section}&s=0"
    response = requests.get(url)

    assert response.status_code == 200, \
        f'Cannot get data from {url}: HTTP response code {response.status_code}'

    response.encoding = 'utf-8'
    text = unescape(response.text)
    return text


def parse_single_table(text):
    """
    Uses regex to retrieve the data + columns used to create one html table.
    Returns a pandas dataframe
    """

    data = re.search('\"data\":(\[\[.+\]\])', text).group(1)
    data = re.findall('(\[[^[]+\])[,\]]', data)
    data = [re.findall("\[(.+)\]", x)[0].split(',') for x in data]
    columns = re.findall('<th>(.+?)<\\\\/th>', text)

    assert len(data) == len(columns) > 1, 'Data and columns size do not match'

    df = pd.DataFrame(data).T
    df.columns = columns
    df.replace('null', np.nan, inplace=True)

    return df


def parse_geral(text):
    """
    Parses GET response from 'Geral' into a long-format pandas DataFrame
    :param text: text output of GET request to 'Geral'
    :return: pd.DataFrame
    """

    df = parse_single_table(text)
    df = df.melt(id_vars='Data', var_name='Ano', value_name='geral_pais')
    df.index = clean_datas(df['Data'], df['Ano'])
    df.drop(columns=['Data', 'Ano'], inplace=True)

    return df


def find_tabs(text):
    tabs = re.findall('\<(div\sclass=\"tab-pane?\s?\w*\"\sdata-value=\".+?(?=\/table))',
                      text, re.DOTALL)
    return tabs


def clean_datas(mmdd, year):
    """
    Combines 2 columns with "mm-dd" and "year" into a single column
    :param mmdd: pd.Series with dates in format "Jan-01"
    :param year: pd.Series with years
    :return: pd.Series in format "01-01-2020"
    """

    months = {'Jan': '01', 'Fev': '02', 'Mar': '03', 'Abr': '04',
              'Mai': '05', 'Jun': '06', 'Jul': '07', 'Ago': '08',
              'Set': '09', 'Out': '10', 'Nov': '11', 'Dez': '12'}

    try:
        md = mmdd.apply(lambda x: x.strip('"').split('-'))
        md = md.apply(lambda x: f"{x[1]}-{months[x[0]]}")
    except:
        raise Exception('Cannot process datas')

    return md + '-' + year


def create_calendar(start):
    """
    Returns a pd.Series with consecutive days between [start] and today
    """

    dates = []
    d = datetime.datetime.strptime(start, "%d-%m-%Y")

    while d < datetime.datetime.today():
        dates.append(d)
        d += datetime.timedelta(1)

    dates = pd.Series([x.strftime("%d-%m-%Y") for x in dates])

    return dates

def parse_multiyear_tabs(text):
    """
    For pages with a multiple tab structure (one tab / Ano)
    Calls parse_single_tab for each tab, adds a column with the respective year.
    Returns a single pandas dataframe
    """

    tabs = find_tabs(text)

    tmp = []
    for t in tabs:
        df = parse_single_table(t)
        year = re.findall('data-value="(\d{4})"\s', t)[0]
        assert 2000 < int(year) < 2100, f'Cannot process year: {year}'
        df['Ano'] = year
        tmp.append(df)

    df = pd.concat(tmp)
    df.index = clean_datas(df['Data (mm-dd)'], df['Ano'])
    df.drop(columns=['Data (mm-dd)', 'Ano'], inplace=True)

    return df


def parse_ars_tabs(text):
    """
    For pages with a multiple tab structure (one tab / ARS)
    Calls parse_single_tab for each tab, adds a column with the respective year.
    Returns a single pandas dataframe
    """

    tabs = find_tabs(text)

    tmp = []
    for t in tabs:
        df = parse_single_table(t)
        df = df.melt(id_vars='Data (mm-dd)', var_name='Ano', value_name='Óbitos')
        df['Data'] = clean_datas(df['Data (mm-dd)'], df['Ano'])
        df.drop(columns=['Data (mm-dd)', 'Ano'], inplace=True)
        df.dropna(inplace=True)
        ARS = re.findall('data-value="(.+)"\s', t)[0]
        df['ARS'] = ARS
        tmp.append(df)

    df = pd.concat(tmp)
    df = df.pivot(index='Data', columns='ARS', values='Óbitos')

    return df


def parse_concelhos(text):
    tabs = find_tabs(text)

    tmp = []
    for t in tabs:
        df = parse_single_table(t)
        df.set_index('Concelho', inplace=True)
        df = df.T
        tmp.append(df)

    assert (all([all(tmp[0].columns == x.columns) for x in tmp])), \
        'Concelhos are not the same in the different tabs'

    df = pd.concat(tmp)

    df.columns = [simplify_unicode(x.lower()
                                   .replace('"', ''))
                  for x in df.columns]
    df.index = [x.replace('Semana', '') for x in df.index]

    return df


def simplify_unicode(x):
    return unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode()


def rename_columns(x, data_source):

    prefixes = {
        'causas': 'causa',
        'idades': 'grupoetario',
        'externas': 'causaexterna',
        'local': 'local',
        'distrito': 'distrito',
        'ACES': 'aces',
        'ARS': 'ars'
    }

    if data_source == 'ACES':
        x = x.replace("ACES ", "")\
            .replace("CS ", "")

    if data_source == 'idades':
        x = x.replace('-', 'a')\
            .replace('<', '')

    if data_source == 'local':
        x = x.replace('Na Instituic?o de Saude', 'instituicaosaude')\
            .replace('No domicilio', 'domicilio')

    x = x.lower()\
        .replace(" ", "")\
        .replace('"', '')

    x = simplify_unicode(x)

    return f"""{prefixes[data_source]}_{x}"""


if __name__ == '__main__':

    ### mortalidade_concelhos.csv

    df = get_data('concelho')
    df = parse_concelhos(df)
    df.to_csv('mortalidade_concelhos.csv', index_label='Semana', encoding='utf-8')

    ### mortalidade.csv

    tables = []

    for t in ['geral', 'idades', 'causas', 'externas', 'local',  'ARS', 'distrito', 'ACES']:

        df = get_data(t)

        if t == 'geral':
            df = parse_geral(df)
        else:
            if t == 'ARS':
                df = parse_ars_tabs(df)
            else:
                df = parse_multiyear_tabs(df)
                if t in ['distrito', 'ACES']:
                    df.rename(str.lower, axis='columns', inplace=True)
                    df = df.pivot(columns=t.lower(), values='óbitos')
            df.columns = [rename_columns(x, t) for x in df.columns]

        tables.append(df)

    df = pd.DataFrame(index=create_calendar(start=tables[0].index[0]),
                      data=tables[0])

    df = df.join(tables[1:], how='left')

    df = df[: -1] # remove last (current) day
    df.to_csv('mortalidade.csv', index_label='Data', encoding='utf-8')
