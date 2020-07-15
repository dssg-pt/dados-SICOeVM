# Imports

from pathlib import Path
import pytest
import csv
import pandas as pd

# Constants
NULL_PLACEHOLDER_VALUE = "NOO"

# Tests fixture (.csv with SICO-eVM data)
@pytest.fixture(scope="module")
def data_mortality():
    r"""
    Loads the CSV with the SICO-eVM
    """

    # Loading the CSV
    current_dir = Path(__file__).parent.absolute()
    csv_filepath = current_dir / ".." / "mortalidade.csv"
    data = pd.read_csv(
        csv_filepath,
        parse_dates=[0],
        dayfirst=True,
        infer_datetime_format=True,
        skip_blank_lines=False
    )

    # Filling NaNs with value zero
    data.fillna(value=NULL_PLACEHOLDER_VALUE, inplace=True)

    # Returning
    return data

def test_number_of_column(data_mortality):
    """
    The generated CSV should always have the same number of columns: 145
    """
    for i, row in data_mortality.iterrows(): 
        assert len(row) == 145

def test_sequentiality_dates(data_mortality):
    """
    Tests if the dates are sequentional by month or day
    """

    for i, row in data_mortality.iterrows(): 

        if i >= 1:
            today_date = data_mortality.iloc[i]["Data"]
            yesterday_date = data_mortality.iloc[i-1]["Data"]
            diff_date = (today_date - yesterday_date).days
            assert diff_date == 1


