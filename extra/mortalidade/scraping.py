import os
import requests
from html import unescape
import re
import datetime
import numpy as np
import pandas as pd
import unicodedata

import logging

##########
# Logging
#
log_filename = os.getcwd() + "extra/mortalidade/logs/scraping.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)

logger = logging.getLogger("scraping")
file_handler = logging.FileHandler(log_filename)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
##########


class MortalityReport:
    """
    Responsible to create a report file to 
    write the status of the last scrapping
    """

    def __init__(self):
        self.__prepare_report()
        self.responses = []
        self.start_time = datetime.datetime.now()

    def __prepare_report(self):
        """
        Creates a file to report the health of the current data scraping
        """

        today = datetime.datetime.today().strftime("%Y-%m-%d-%H:%M")

        report_path = os.getcwd() + "/extra/mortalidade/reports"

        self.report_file = f"{report_path}/report_{today}.txt"
        os.makedirs(os.path.dirname(self.report_file), exist_ok=True)

        with open(self.report_file, "w+") as report:
            report.write(f"Scrapping date: {today}\n")

    def __write_responses_status(self):

        with open(self.report_file, "a") as report:
            report.write("\n- Verificação de Respostas HTTP:")
            for response in self.responses:
                section, res = response

                report.write(f"\n\tSecção: '{section}'")
                report.write(
                    f"\n\t\tRequest: 'https://evm.min-saude.pt/table?t={section}&s=0'"
                )
                report.write(f"\n\t\tResponse: [{res.status_code}]")

    def __write_process_time(self):

        process_time = datetime.datetime.now() - self.start_time

        with open(self.report_file, "a") as report:
            report.write(f"\n- Tempo dispendido: {process_time}")

    def check_all_districts(self, districts):
        """
        Checks if all expected districts were collected

        :param districts: The scrapped
        """

        expected_districts = pd.read_csv(
            os.getcwd() + "/extra/mortalidade/facts/concelhos.csv"
        )

        missing_districts = []

        # Checks for missing districts
        for district in expected_districts:
            if not district in districts:
                missing_districts.append(district)
                logger.error(
                    f"[check_all_districts] Expected district not found: {district}"
                )

        # Writes into the report
        with open(self.report_file, "a") as report:
            report.write("- Verificação de concelhos:")
            if missing_districts:
                report.write("\t[FAILED]\n")
                report.write("\tMissing Districts:\n")
                report.write(",".join(missing_districts))
            else:
                report.write("\t[SUCCESS]")

    def check_get_data(self, section, response):

        logger.info(
            f"[get_data({section})] - Request: 'https://evm.min-saude.pt/table?t={section}&s=0' | Response: {response}"
        )

        self.responses.append((section, response))

    def close(self):

        self.__write_responses_status()
        self.__write_process_time()


class MortalityScrapping:
    """
    Class to manage scrapping of the Mortalities in Portugal
    Source of data from SICO-eVM
    """

    def __init__(self):
        self.report = MortalityReport()

    def start(self):

        self.__get_mortalidade_concelhos()
        self.__get_mortalidade()
        self.__close()

    def __close(self):
        self.report.close()

    def __get_mortalidade_concelhos(self, csv_export_file="mortalidade_concelhos.csv"):
        """
        Grabs all information from "Concelhos" and
            exports it to 'mortalidade_concelhos.csv'
        """

        df = self.__get_data("concelho")
        df = self.__parse_concelhos(df)

        df.to_csv(csv_export_file, index_label="Semana", encoding="utf-8")

    def __get_mortalidade(self, csv_export_file="mortalidade.csv"):
        """
        Grabs all information regarding mortality 
            exports it to file [csv_export_file]
        """

        tables = []

        for t in [
            "geral",
            "idades",
            "causas",
            "externas",
            "local",
            "ARS",
            "distrito",
            "ACES",
        ]:

            df = self.__get_data(t)

            if t == "geral":
                df = self.__parse_geral(df)
            else:
                if t == "ARS":
                    df = self.__parse_ars_tabs(df)
                else:
                    df = self.__parse_multiyear_tabs(df)
                    if t in ["distrito", "ACES"]:
                        df.rename(str.lower, axis="columns", inplace=True)
                        df = df.pivot(columns=t.lower(), values="óbitos")
                df.columns = [self.__rename_columns(x, t) for x in df.columns]

            tables.append(df)

        df = pd.DataFrame(
            index=self.__create_calendar(start=tables[0].index[0]), data=tables[0]
        )

        df = df.join(tables[1:], how="left")

        df = df[:-1]  # remove last (current) day
        df.to_csv(csv_export_file, index_label="Data", encoding="utf-8")

    def __get_data(self, section):
        """
        Makes GET request to the respective [section] of the eVM,
        fixes html encodings and returns the html
        """

        url = f"https://evm.min-saude.pt/table?t={section}&s=0"
        response = requests.get(url)

        self.report.check_get_data(section, response)
        assert (
            response.ok
        ), f"Cannot get data from {url}: HTTP response code {response.status_code}"

        response.encoding = "utf-8"
        text = unescape(response.text)
        return text

    def __parse_single_table(self, text):
        """
        Uses regex to retrieve the data + columns used to create one html table.
        Returns a pandas dataframe
        """

        data = re.search('"data":(\[\[.+\]\])', text).group(1)
        data = re.findall("(\[[^[]+\])[,\]]", data)
        data = [re.findall("\[(.+)\]", x)[0].split(",") for x in data]
        columns = re.findall("<th>(.+?)<\\\\/th>", text)

        assert len(data) == len(columns) > 1, "Data and columns size do not match"

        df = pd.DataFrame(data).T
        df.columns = columns
        df.replace("null", np.nan, inplace=True)

        return df

    def __parse_geral(self, text):
        """
        Parses GET response from 'Geral' into a long-format pandas DataFrame
        :param text: text output of GET request to 'Geral'
        :return: pd.DataFrame
        """

        df = self.__parse_single_table(text)
        df = df.melt(id_vars="Data", var_name="Ano", value_name="geral_pais")
        df.index = self.__clean_datas(df["Data"], df["Ano"])
        df.drop(columns=["Data", "Ano"], inplace=True)

        return df

    def __find_tabs(self, text):
        tabs = re.findall(
            '\<(div\sclass="tab-pane?\s?\w*"\sdata-value=".+?(?=\/table))',
            text,
            re.DOTALL,
        )

        return tabs

    def __clean_datas(self, mmdd, year):
        """
        Combines 2 columns with "mm-dd" and "year" into a single column
        :param mmdd: pd.Series with dates in format "Jan-01"
        :param year: pd.Series with years
        :return: pd.Series in format "01-01-2020"
        """

        months = {
            "Jan": "01",
            "Fev": "02",
            "Mar": "03",
            "Abr": "04",
            "Mai": "05",
            "Jun": "06",
            "Jul": "07",
            "Ago": "08",
            "Set": "09",
            "Out": "10",
            "Nov": "11",
            "Dez": "12",
        }

        try:
            md = mmdd.apply(lambda x: x.strip('"').split("-"))
            md = md.apply(lambda x: f"{x[1]}-{months[x[0]]}")
        except:
            raise Exception("Cannot process datas")

        return md + "-" + year

    def __create_calendar(self, start):
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

    def __parse_multiyear_tabs(self, text):
        """
        For pages with a multiple tab structure (one tab / Ano)
        Calls parse_single_tab for each tab, adds a column with the respective year.
        Returns a single pandas dataframe
        """

        tabs = self.__find_tabs(text)

        tmp = []
        for t in tabs:
            df = self.__parse_single_table(t)
            year = re.findall('data-value="(\d{4})"\s', t)[0]
            assert 2000 < int(year) < 2100, f"Cannot process year: {year}"
            df["Ano"] = year
            tmp.append(df)

        df = pd.concat(tmp)
        df.index = self.__clean_datas(df["Data (mm-dd)"], df["Ano"])
        df.drop(columns=["Data (mm-dd)", "Ano"], inplace=True)

        return df

    def __parse_ars_tabs(self, text):
        """
        For pages with a multiple tab structure (one tab / ARS)
        Calls parse_single_tab for each tab, adds a column with the respective year.
        Returns a single pandas dataframe
        """

        tabs = self.__find_tabs(text)

        tmp = []
        for t in tabs:
            df = self.__parse_single_table(t)
            df = df.melt(id_vars="Data (mm-dd)", var_name="Ano", value_name="Óbitos")
            df["Data"] = self.__clean_datas(df["Data (mm-dd)"], df["Ano"])
            df.drop(columns=["Data (mm-dd)", "Ano"], inplace=True)
            df.dropna(inplace=True)
            ARS = re.findall('data-value="(.+)"\s', t)[0]
            df["ARS"] = ARS
            tmp.append(df)

        df = pd.concat(tmp)
        df = df.pivot(index="Data", columns="ARS", values="Óbitos")

        return df

    def __parse_concelhos(self, text):
        """
        Parses from a raw text to a Pandas Dataframe type with 
                all 'concelhos' to be worked on.

        :param text: raw html in text

        :return: pd.DataFrame
        """
        tabs = self.__find_tabs(text)

        tmp = []
        for t in tabs:
            df = self.__parse_single_table(t)
            df.set_index("Concelho", inplace=True)
            df = df.T
            tmp.append(df)

        assert all(
            [all(tmp[0].columns == x.columns) for x in tmp]
        ), "Concelhos are not the same in the different tabs"

        df = pd.concat(tmp)

        df.columns = [
            self.__simplify_unicode(x.lower().replace('"', "")) for x in df.columns
        ]
        df.index = [x.replace("Semana", "") for x in df.index]

        self.report.check_all_districts(df.columns)
        return df

    def __simplify_unicode(self, x):
        return unicodedata.normalize("NFD", x).encode("ascii", "ignore").decode()

    def __rename_columns(self, x, data_source):

        prefixes = {
            "causas": "causa",
            "idades": "grupoetario",
            "externas": "causaexterna",
            "local": "local",
            "distrito": "distrito",
            "ACES": "aces",
            "ARS": "ars",
        }

        if data_source == "ACES":
            x = x.replace("ACES ", "").replace("CS ", "")

        if data_source == "idades":
            x = x.replace("-", "a").replace("<", "")

        if data_source == "local":
            x = x.replace("Na Instituic?o de Saude", "instituicaosaude").replace(
                "No domicilio", "domicilio"
            )

        x = x.lower().replace(" ", "").replace('"', "")

        x = self.__simplify_unicode(x)

        return f"""{prefixes[data_source]}_{x}"""


if __name__ == "__main__":

    scrap = MortalityScrapping()
    scrap.start()

