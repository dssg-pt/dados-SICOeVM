import requests
from html import unescape
import re
from numpy import nan
import pandas as pd

months = {'Jan': '01', 'Fev': '02', 'Mar': '03', 'Abr': '04',
          'Mai': '05', 'Jun': '06', 'Jul': '07', 'Ago': '08',
          'Set': '09', 'Out': '10', 'Nov': '11', 'Dez': '12'}


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


def parse_single_tab(text):
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


def parse_multiple_tabs(text):
    """
    For pages with a multiple tab structure (one tab / Ano)
    Calls parse_single_tab for each tab, adds a column with the respective year.
    Returns a single pandas dataframe
    """

    tabs = re.findall('\<(div\sclass=\"tab-pane\"\sdata-value=\"20\d\d.+?(?=\/table))',
                      text, re.DOTALL)

    tmp = []
    for t in tabs:
        df = parse_single_tab(t)
        year = re.findall('data-value="(\d{4})"\s', t)
        df['Ano'] = year[0]
        df['Data'] = df.apply(lambda x: '-'.join([x['Ano'], x['Data (mm-dd)'].replace('"', '')]), axis=1)
        df.drop(columns=['Data (mm-dd)', 'Ano'], inplace=True)
        tmp.append(df)

    return pd.concat(tmp)
