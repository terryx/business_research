# helper.py
import requests
import json
import yaml
import time
import pandas as pd
from typing import Literal

# Read config from yaml file
def load_config():
    """
    Loads all values from a YAML file and returns them as a Python dictionary.

    Parameters:
    - yaml_file (str): The path to the YAML file.

    Returns:
    - dict: The contents of the YAML file as a Python dictionary.
    """
    # Load the YAML file and return the entire content as a dictionary
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

# Define HTTP request, symbols and functions
def fetch_and_save(ticker, financial, api_key):
    base_url = 'https://www.alphavantage.co/query'

    params = {
        'function': financial,
        'symbol': ticker,
        'apikey': api_key
    }

    response = requests.get(base_url, params=params)

    # Add a 250ms delay to avoid hitting the rate limit
    time.sleep(0.25)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Check for rate limit response
        if info := data.get('Information'):
            raise ValueError(info)

        with open(f'../../data/fundamental/{ticker}-{financial}.json', 'w') as json_file: # type: ignore
            json.dump(data, json_file, indent=4)

    else:
        raise response.raise_for_status()

def consolidate_financials(symbols, functions, period: Literal["Q", "Y"]):
    """
    Consolidates financial data from multiple sources into a single report.

    Parameters:
    symbols (list): A list of financial symbols (e.g., stock tickers) to retrieve data for.
    functions (list): A list of functions that define the type of financial data to extract (e.g., balance sheet, income statement).
    period (Literal["Q", "Y"]): Specifies the reporting period for the data:
        - "Q" for quarterly reports
        - "Y" for annual (yearly) reports

    The function gathers financial data based on the provided symbols and functions, then consolidates
    them into a unified report for the specified period (quarterly or annual).
    """
    report_type = "annualReports"
    earning_type = "annualEarnings"

    report_data_dict = {}

    if period == "Q":
        report_type = "quarterlyReports"
        earning_type = "quarterlyEarnings"

    for symbol in symbols:
        for function in functions:

            file_path = f'../../data/fundamental/{symbol}-{function}.json'

            # Open and load the JSON file
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)

            # Extract the 'annualReports' data
            report_data = data.get(report_type, [])

            if not report_data:
                report_data = data.get(earning_type, [])

            # Loop through the report data and reformat it
            for item in report_data:
                fiscal_date = item.get('fiscalDateEnding')
                # Add each key-value pair to the dictionary
                for key, value in item.items():
                    # if key != 'fiscalDateEnding':
                    if key not in report_data_dict:
                        report_data_dict[key] = {}
                    report_data_dict[key][fiscal_date] = value

            # Convert the dictionary to a DataFrame
            df = pd.DataFrame(report_data_dict).T

            df = df.apply(pd.to_numeric, errors='coerce')

            df = df.fillna(0)

            df.to_json(f'../../data/consolidated/{symbol}.json', indent=4)

# Function to highlight DataFrame rows based on thresholds
def highlight_ratio(s, margins):
    """
    Highlights a DataFrame series based on margins dictionary.

    Parameters:
    s: pd.Series
        The row (series) to highlight.
    margins: dict
        A dictionary with margin names, thresholds, and comparison types.

    Returns:
    list
        A list of background-color styles based on the conditions.
    """
    # Check if the series name exists in the margins configuration
    if s.name in margins:
        config = margins[s.name]
        threshold = config['threshold']
        comparison = config['comparison']

        # Apply the appropriate comparison
        if comparison == 'greater':
            return ['background-color: green' if val > threshold else 'background-color: red' for val in s]
        elif comparison == 'less':
            return ['background-color: green' if val < threshold else 'background-color: red' for val in s]