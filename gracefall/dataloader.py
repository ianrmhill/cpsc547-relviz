"""Helper functions for importing and reformatting data for use with the visualization tool."""

import json
import pandas as pd


def load_gerabaldi_report(file: str = None):
    """Load in a test report exported from the Gerabaldi simulator."""
    if file:
        with open(file, 'r') as f:
            json_rprt = json.load(f)
    else:
        raise Exception('No report to load specified')
    # Convert the pandas dataframes
    json_rprt['Measurements'] = pd.read_json(json_rprt['Measurements'])
    json_rprt['Stress Summary'] = pd.read_json(json_rprt['Stress Summary'])
    return json_rprt
