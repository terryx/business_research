# helper.py
import requests
import json
import yaml

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