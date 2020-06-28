import requests
from html import unescape
import re
from numpy import nan
import pandas as pd


def get_data(section):
    """
    Makes GET request to the respective [section] of the eVM,
    fixes html encodings and returns the html
    """

    url = f"https://evm.min-saude.pt/table?t={section}&s=0"
    response = requests.get(url)
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

    df = pd.DataFrame(data).T
    df.columns = columns
    df.replace('null', nan, inplace=True)

    return df


def parse_geral(text):
    """
    Parses GET response from 'Geral' into a long-format pandas DataFrame
    :param text: text output of GET request to 'Geral'
    :return: pd.DataFrame
    """

    df = parse_single_table(text)
    df = df.melt(id_vars='Data', var_name='Ano', value_name='mortes')
    df['data'] = clean_datas(df['Data'], df['Ano'])
    df.drop(columns=['Data', 'Ano'], inplace=True)
    df.dropna(inplace=True)

    return df


def find_tabs(text):
    tabs = re.findall('\<(div\sclass=\"tab-pane?\s?\w*\"\sdata-value=\"20\d\d.+?(?=\/table))',
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

    md = mmdd.apply(lambda x: x.strip('"').split('-'))
    md = md.apply(lambda x: f"{x[1]}-{months[x[0]]}")

    return md + '-' + year


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
        year = re.findall('data-value="(\d{4})"\s', t)
        df['Ano'] = year[0]
        tmp.append(df)

    df = pd.concat(tmp)
    df['data'] = clean_datas(df['Data (mm-dd)'], df['Ano'])
    df.drop(columns=['Data (mm-dd)', 'Ano'], inplace=True)

    return df


def parse_concelhos(text):

    tabs = find_tabs(text)

    tmp = []
    for t in tabs:
        df = parse_single_table(t)
        df.set_index('Concelho', inplace=True)
        df = df.T
        tmp.append(df)

    df = pd.concat(tmp) #TODO test if columns are the same
    df.columns = [x.replace('"', '') for x in df.columns]
    df.index = [x.replace('Semana', '') for x in df.index]

    return df